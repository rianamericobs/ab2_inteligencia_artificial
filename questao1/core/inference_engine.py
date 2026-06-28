"""
Módulo: Motor de Inferência
Implementa Encadeamento para Frente, para Trás e Estratégia Híbrida.
Rastreia toda a cadeia de inferência para o mecanismo de explicação.
"""
from dataclasses import dataclass, field
from typing import Optional, Callable, Any
from .knowledge_base import KnowledgeBase, Rule, Fact


# ─── Registro de Inferência (para explicações) ────────────────────────────────

@dataclass
class InferenceStep:
    """Registra um passo de inferência."""
    rule_id: str
    rule_repr: str
    conditions_met: list[str]
    conclusion: str
    strategy: str          # "forward" | "backward"
    cf: float = 1.0


@dataclass
class InferenceTrace:
    """Trilha completa de inferência de uma sessão."""
    steps: list[InferenceStep] = field(default_factory=list)
    questions_asked: dict[str, str] = field(default_factory=dict)  # atributo → motivo
    goal_stack: list[str] = field(default_factory=list)            # pilha de objetivos BC

    def record_step(self, rule: Rule, strategy: str, cf: float = 1.0):
        step = InferenceStep(
            rule_id=rule.id,
            rule_repr=str(rule),
            conditions_met=[str(c) for c in rule.conditions],
            conclusion=str(rule.conclusion),
            strategy=strategy,
            cf=cf
        )
        self.steps.append(step)

    def record_question(self, attribute: str, reason: str):
        self.questions_asked[attribute] = reason

    def rules_that_concluded(self, attribute: str, value=None) -> list[InferenceStep]:
        if value and " (cf:" in str(value).lower():
            idx = str(value).lower().rfind(" (cf:")
            value = value[:idx].strip()
            
        result = []
        for s in self.steps:
            attr_part = s.conclusion.split("=")[0].strip()
            val_part = s.conclusion.split("=")[1].strip() if "=" in s.conclusion else ""
            if " (cf:" in val_part.lower():
                idx_v = val_part.lower().rfind(" (cf:")
                val_part = val_part[:idx_v].strip()
                
            if attr_part == attribute:
                if value is None or str(value).lower() == val_part.lower():
                    result.append(s)
        return result


# ─── Motor ────────────────────────────────────────────────────────────────────

class InferenceEngine:
    def __init__(self, kb: KnowledgeBase,
                 ask_user_callback: Optional[Callable[[str, str, list], Optional[str]]] = None):
        """
        kb: base de conhecimento
        ask_user_callback: função(atributo, pergunta, opcoes) → resposta ou None
        """
        self.kb = kb
        self.ask_user = ask_user_callback
        self.trace = InferenceTrace()
        self._max_cycles = 200   # segurança contra loop infinito

    def reset(self):
        self.trace = InferenceTrace()
        self.kb.reset_session()

    def _evaluate_rule_cf(self, rule: Rule) -> float:
        if not rule.conditions:
            return rule.cf * rule.conclusion.cf
        cfs = []
        for c in rule.conditions:
            fact = self.kb.get_fact(c.attribute)
            cfs.append(fact.cf if fact else 0.0)
        
        premise_cf = max(cfs) if rule.condition_operator == "OR" else min(cfs)
        return premise_cf * rule.cf * rule.conclusion.cf

    def _assert_or_combine_fact(self, attribute: str, value: Any, cf: float, source: str, rule_id: Optional[str] = None) -> bool:
        existing = self.kb.get_fact(attribute)
        if existing:
            if str(existing.value).lower() == str(value).lower():
                old_cf = existing.cf
                new_cf = old_cf + cf - (old_cf * cf)
                existing.cf = new_cf
                return (new_cf - old_cf) > 0.001
            return False
        self.kb.assert_fact(attribute, value, source=source, rule_id=rule_id, cf=cf)
        return True

    # ── Encadeamento para Frente ───────────────────────────────────────────────

    def forward_chain(self) -> list[str]:
        new_conclusions: list[str] = []
        fired_rules: set[str] = {s.rule_id for s in self.trace.steps}
        changed = True
        cycles = 0
        while changed and cycles < self._max_cycles:
            changed = False
            cycles += 1
            for rule in self.kb.get_rules_sorted():
                if rule.id not in fired_rules and rule.is_applicable(self.kb.facts_dict()):
                    rule_cf = self._evaluate_rule_cf(rule)
                    conc_attr = rule.conclusion.attribute
                    conc_val = rule.conclusion.value
                    
                    if self._assert_or_combine_fact(conc_attr, conc_val, cf=rule_cf, source="inferred", rule_id=rule.id):
                        self.trace.record_step(rule, "forward", rule_cf)
                        new_conclusions.append(f"{conc_attr} = {conc_val} (CF: {rule_cf:.2f})")
                        changed = True
                        fired_rules.add(rule.id)
        return new_conclusions

    # ── Encadeamento para Trás ─────────────────────────────────────────────────

    def backward_chain(self, goal_attribute: str, goal_value: Optional[str] = None) -> bool:
        self.trace.goal_stack.append(goal_attribute)
        try:
            relevant_rules = [
                r for r in self.kb.get_rules_sorted()
                if r.conclusion.attribute == goal_attribute
                and (goal_value is None or str(r.conclusion.value).lower() == str(goal_value).lower())
            ]

            proved_any = False
            for rule in relevant_rules:
                if self._try_rule_backward(rule):
                    proved_any = True

            if proved_any:
                return True

            current = self.kb.get_fact(goal_attribute)
            if current is not None:
                if goal_value is None or str(current.value).lower() == str(goal_value).lower():
                    return True

            if goal_attribute in self.kb.questions and self.ask_user:
                if goal_attribute in self.trace.questions_asked:
                    return False
                
                question = self.kb.questions[goal_attribute]
                options = self.kb.answer_options.get(goal_attribute, [])
                reason = self._build_why_reason(goal_attribute)
                self.trace.record_question(goal_attribute, reason)
                answer = self.ask_user(goal_attribute, question, options)
                if answer is not None:
                    # CLI support (if callback didn't assert)
                    if not self.kb.get_fact(goal_attribute):
                        self.kb.assert_fact(goal_attribute, answer, source="user", cf=1.0)
                    return True
            return False
        finally:
            if self.trace.goal_stack and self.trace.goal_stack[-1] == goal_attribute:
                self.trace.goal_stack.pop()

    def _try_rule_backward(self, rule: Rule) -> bool:
        if any(s.rule_id == rule.id for s in self.trace.steps):
            return True
        for condition in rule.conditions:
            current = self.kb.get_fact(condition.attribute)
            if current is None:
                if condition.attribute in self.trace.questions_asked:
                    if rule.condition_operator == "AND":
                        return False
                    continue
                
                proved = self.backward_chain(condition.attribute)
                if not proved:
                    if condition.attribute in self.trace.questions_asked:
                        if rule.condition_operator == "AND":
                            return False
                        continue
                    
                    if condition.attribute in self.kb.questions and self.ask_user:
                        question = self.kb.questions[condition.attribute]
                        options = self.kb.answer_options.get(condition.attribute, [])
                        reason = self._build_why_reason(condition.attribute)
                        self.trace.record_question(condition.attribute, reason)
                        answer = self.ask_user(condition.attribute, question, options)
                        if answer is not None:
                            if not self.kb.get_fact(condition.attribute):
                                self.kb.assert_fact(condition.attribute, answer, source="user", cf=1.0)
                        else:
                            if rule.condition_operator == "AND":
                                return False
                    else:
                        if rule.condition_operator == "AND":
                            return False
            if not condition.evaluate(self.kb.facts_dict()) and rule.condition_operator == "AND":
                return False

        if rule.is_applicable(self.kb.facts_dict()):
            rule_cf = self._evaluate_rule_cf(rule)
            self._assert_or_combine_fact(rule.conclusion.attribute, rule.conclusion.value, cf=rule_cf, source="inferred", rule_id=rule.id)
            self.trace.record_step(rule, "backward", rule_cf)
            return True
        return False

    # ── Estratégia Híbrida ────────────────────────────────────────────────────

    def hybrid_chain(self, hypotheses: Optional[list[str]] = None) -> dict[str, list[str]]:
        self.forward_chain()

        targets = hypotheses or self.kb.hypotheses
        if not targets:
            targets = list({r.conclusion.attribute for r in self.kb.rules.values()})
            
        results: dict[str, list[str]] = {}

        for hyp_attr in targets:
            current = self.kb.get_fact(hyp_attr)
            if current is not None:
                results[hyp_attr] = [f"{current.value} (CF: {current.cf:.2f})"]
                continue
            
            self.backward_chain(hyp_attr)
            
            val = self.kb.get_fact(hyp_attr)
            if val is not None:
                results[hyp_attr] = [f"{val.value} (CF: {val.cf:.2f})"]
            else:
                possible = []
                for r in self.kb.get_rules_sorted():
                    if r.conclusion.attribute == hyp_attr:
                        val_r = self.kb.get_fact(r.conclusion.attribute)
                        if val_r is not None:
                            possible.append(f"{val_r.value} (CF: {val_r.cf:.2f})")
                results[hyp_attr] = possible if possible else []

        self.forward_chain()

        for hyp_attr in targets:
            val = self.kb.get_fact(hyp_attr)
            if val is not None and hyp_attr not in results:
                results[hyp_attr] = [f"{val.value} (CF: {val.cf:.2f})"]

        return results

    # ── Utilitários ────────────────────────────────────────────────────────────

    def _build_why_reason(self, attribute: str) -> str:
        """Constrói a justificativa para perguntar sobre um atributo."""
        goals = list(self.trace.goal_stack)
        if goals:
            current_goal = goals[-1] if goals[-1] != attribute else (goals[-2] if len(goals) > 1 else None)
            if current_goal:
                # Encontrar regras que usam este atributo para provar o objetivo
                relevant = [
                    r for r in self.kb.get_rules_sorted()
                    if any(c.attribute == attribute for c in r.conditions)
                    and r.conclusion.attribute == current_goal
                ]
                if relevant:
                    return (f"Estou avaliando a hipótese '{current_goal}' e o atributo "
                            f"'{attribute}' é uma condição necessária na(s) regra(s): "
                            + ", ".join(r.id for r in relevant))
        return f"O atributo '{attribute}' é necessário para continuar o diagnóstico."

    def applicable_rules(self) -> list[Rule]:
        """Retorna regras que podem ser disparadas com os fatos atuais."""
        return [r for r in self.kb.get_rules_sorted()
                if r.is_applicable(self.kb.facts_dict())]

    def potentially_applicable_rules(self) -> list[Rule]:
        """Regras que poderiam ser disparadas se mais fatos fossem conhecidos."""
        facts = self.kb.facts_dict()
        result = []
        for r in self.kb.get_rules_sorted():
            known = [c for c in r.conditions if c.attribute in facts]
            if known and not r.is_applicable(facts):
                result.append(r)
        return result
