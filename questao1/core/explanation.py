"""
Módulo: Mecanismo de Explicação
Responde às perguntas "Por quê?" e "Como?" durante a consulta.
"""
from .inference_engine import InferenceEngine, InferenceTrace
from .knowledge_base import KnowledgeBase


class ExplanationEngine:
    def __init__(self, kb: KnowledgeBase, engine: InferenceEngine):
        self.kb = kb
        self.engine = engine

    @property
    def trace(self) -> InferenceTrace:
        return self.engine.trace

    # ── Por quê? ──────────────────────────────────────────────────────────────

    def why(self, attribute: str) -> str:
        """Explica por que determinada pergunta foi feita ao usuário."""
        reason = self.trace.questions_asked.get(attribute)
        if reason:
            return f"[POR QUÊ '{attribute}' foi perguntado]\n{reason}"

        # Buscar regras que dependem deste atributo
        dependent_rules = [
            r for r in self.kb.rules.values()
            if any(c.attribute == attribute for c in r.conditions)
        ]
        if not dependent_rules:
            return (f"[POR QUÊ '{attribute}' foi perguntado]\n"
                    f"O atributo '{attribute}' é necessário para avaliação, "
                    f"mas não há regras explícitas registradas.")

        lines = [f"[POR QUÊ '{attribute}' foi perguntado]",
                 f"O atributo '{attribute}' aparece nas condições das seguintes regras:"]
        for r in dependent_rules:
            hyp = r.conclusion.attribute
            lines.append(f"  • {r.id} ({r.name}): usada para concluir '{hyp} = {r.conclusion.value}'")
        if self.trace.goal_stack:
            lines.append(f"\nO objetivo atual na pilha de inferência é: "
                         f"'{' → '.join(self.trace.goal_stack)}'")
        return "\n".join(lines)

    # ── Como? ─────────────────────────────────────────────────────────────────

    def how(self, attribute: str, value: str = None) -> str:
        if value and " (cf:" in str(value).lower():
            idx = str(value).lower().rfind(" (cf:")
            value = value[:idx].strip()
            
        steps = self.trace.rules_that_concluded(attribute, value)
        
        fact = self.kb.get_fact(attribute)
        val = value or (fact.value if fact else None)
        cf_str = f" (CF: {fact.cf:.2f})" if fact else ""

        if not steps:
            if fact and fact.source == "user":
                return (f"[COMO '{attribute} = {val}'{cf_str} foi obtido]\n"
                        f"Este valor foi informado diretamente pelo usuário durante a consulta.")
            if fact and fact.source == "initial":
                return (f"[COMO '{attribute} = {val}'{cf_str} foi obtido]\n"
                        f"Este valor foi fornecido como fato inicial na base de conhecimento.")
            return (f"[COMO '{attribute} = {val}' foi obtido]\n"
                    f"Não foi possível localizar a cadeia de inferência para este atributo. "
                    f"Verifique se a consulta foi executada.")

        lines = [f"[COMO '{attribute} = {val}'{cf_str} foi obtido]"]
        for i, step in enumerate(steps, 1):
            lines.append(f"\nPasso {i} — Regra {step.rule_id} (estratégia: {step.strategy}):")
            lines.append(f"  Regra: {step.rule_repr}")
            lines.append(f"  Condições satisfeitas:")
            for cond in step.conditions_met:
                lines.append(f"    ✓ {cond}")
            lines.append(f"  Conclusão inferida: {step.conclusion} com CF {step.cf:.2f}")
        return "\n".join(lines)

    # ── Trilha completa ───────────────────────────────────────────────────────

    def full_trace(self) -> str:
        """Exibe toda a cadeia de inferência da sessão."""
        if not self.trace.steps:
            return "Nenhuma inferência foi realizada nesta sessão."

        lines = ["=" * 60, "TRILHA COMPLETA DE INFERÊNCIA", "=" * 60]
        for i, step in enumerate(self.trace.steps, 1):
            lines.append(f"\n[Passo {i}] Estratégia: {step.strategy.upper()}")
            lines.append(f"  Regra: {step.rule_repr}")
            lines.append(f"  Conclusão: {step.conclusion}")

        if self.trace.questions_asked:
            lines.append("\n" + "─" * 40)
            lines.append("PERGUNTAS REALIZADAS AO USUÁRIO:")
            for attr, reason in self.trace.questions_asked.items():
                val = self.kb.get_fact_value(attr)
                lines.append(f"  • {attr} = {val!r}  (motivo: {reason[:80]}...)")

        return "\n".join(lines)

    # ── Estado da sessão ──────────────────────────────────────────────────────

    def session_summary(self) -> str:
        """Resumo dos fatos e conclusões da sessão atual."""
        lines = ["=" * 60, "RESUMO DA SESSÃO", "=" * 60]

        user_facts = [f for f in self.kb.working_memory.values() if f.source == "user"]
        inferred = [f for f in self.kb.working_memory.values() if f.source == "inferred"]
        initial = [f for f in self.kb.working_memory.values() if f.source == "initial"]

        if initial:
            lines.append("\nFatos Iniciais:")
            for f in initial:
                lines.append(f"  • {f.attribute} = {f.value} (CF: {f.cf:.2f})")
        if user_facts:
            lines.append("\nFatos Informados pelo Usuário:")
            for f in user_facts:
                lines.append(f"  • {f.attribute} = {f.value} (CF: {f.cf:.2f})")
        if inferred:
            lines.append("\nFatos Inferidos:")
            for f in inferred:
                rule_info = f" (via {f.rule_id})" if f.rule_id else ""
                lines.append(f"  • {f.attribute} = {f.value} (CF: {f.cf:.2f}){rule_info}")

        if not user_facts and not inferred:
            lines.append("\nNenhum fato foi coletado ou inferido ainda.")

        return "\n".join(lines)
