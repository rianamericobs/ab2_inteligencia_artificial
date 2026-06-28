"""
Módulo: Base de Conhecimento
Armazena fatos iniciais, fatos inferidos, regras de produção e hipóteses.
"""
import json
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


def normalize_option(val: str, options: list[str]) -> Optional[str]:
    """
    Normaliza deterministicamente uma resposta do usuário contra uma lista de opções válidas.
    Suporta variações comuns de Sim/Não, case-insensitivity e espaços adicionais.
    """
    val_clean = val.strip().lower()
    
    # Mapeamentos comuns para português e inglês
    sim_variants = {"sim", "s", "yes", "y", "true", "confirmar", "confirmado", "1"}
    nao_variants = {"não", "nao", "n", "no", "false", "cancelar", "negado", "0"}
    
    # 1. Correspondência exata case-insensitive
    for opt in options:
        if opt.strip().lower() == val_clean:
            return opt

    # 2. Se a entrada mapear para "sim" e alguma opção for representativa de confirmação
    if val_clean in sim_variants:
        for opt in options:
            if opt.strip().lower() in {"sim", "s", "yes", "y", "true"}:
                return opt
                
    # 3. Se a entrada mapear para "não" e alguma opção for representativa de negação
    if val_clean in nao_variants:
        for opt in options:
            if opt.strip().lower() in {"não", "nao", "n", "no", "false"}:
                return opt
                
    return None


def is_numeric_attribute(kb: 'KnowledgeBase', attribute: str) -> bool:
    """
    Verifica se o atributo é numérico analisando as regras na base de conhecimento.
    Um atributo é numérico se for usado com operadores de comparação (>, <, >=, <=)
    ou se for comparado com um valor que pode ser convertido para float.
    """
    for rule in kb.rules.values():
        for cond in rule.conditions:
            if cond.attribute == attribute:
                if cond.operator in (">", "<", ">=", "<="):
                    return True
                try:
                    float(cond.value)
                    return True
                except ValueError:
                    pass
    return False


def validate_free_input(kb: 'KnowledgeBase', attribute: str, value: str) -> tuple[Optional[str], bool, str]:
    """
    Valida e normaliza uma entrada de texto livre para um atributo que não possui opções explícitas.
    Retorna (valor_normalizado, valido, mensagem_erro).
    """
    val_clean = value.strip()
    
    # 1. Tentar ver se é numérico (suporta vírgula como separador decimal)
    val_normalized = val_clean.replace(",", ".")
    is_numeric = False
    numeric_value = None
    try:
        numeric_value = float(val_normalized)
        is_numeric = True
    except ValueError:
        pass
        
    if is_numeric:
        # Se houver limites cadastrados na KB para o atributo, validar o intervalo
        if attribute in kb.attribute_ranges:
            limits = kb.attribute_ranges[attribute]
            if isinstance(limits, (list, tuple)) and len(limits) == 2:
                min_val = float(limits[0]) if limits[0] is not None else None
                max_val = float(limits[1]) if limits[1] is not None else None
                
                if min_val is not None and numeric_value < min_val:
                    return None, False, format_range_message(min_val, max_val)
                if max_val is not None and numeric_value > max_val:
                    return None, False, format_range_message(min_val, max_val)
                    
        return val_normalized, True, ""
        
    # 2. Se não for numérico, verificar quais são os valores conhecidos na KB para este atributo
    known_values = set()
    has_numeric_comparison = False
    for rule in kb.rules.values():
        for cond in rule.conditions:
            if cond.attribute == attribute:
                known_values.add(str(cond.value).strip().lower())
                if cond.operator in (">", "<", ">=", "<="):
                    has_numeric_comparison = True
                    
    # Se o valor digitado corresponde a um dos valores textuais conhecidos nas regras, aceitar
    if val_clean.lower() in known_values:
        # Encontrar a grafia original do valor na KB
        for rule in kb.rules.values():
            for cond in rule.conditions:
                if cond.attribute == attribute and str(cond.value).strip().lower() == val_clean.lower():
                    return str(cond.value).strip(), True, ""
                    
    # Se não corresponder a nenhum valor conhecido, mas houver comparações numéricas,
    # limites cadastrados ou se todos os valores conhecidos forem numéricos, rejeitamos.
    if has_numeric_comparison or attribute in kb.attribute_ranges:
        if attribute in kb.attribute_ranges:
            limits = kb.attribute_ranges[attribute]
            if isinstance(limits, (list, tuple)) and len(limits) == 2:
                min_val = float(limits[0]) if limits[0] is not None else None
                max_val = float(limits[1]) if limits[1] is not None else None
                return None, False, format_range_message(min_val, max_val)
        return None, False, "espera-se um valor numérico"
        
    # Verificar se todos os valores conhecidos nas regras são numéricos
    only_numeric_in_rules = True
    if known_values:
        for kv in known_values:
            try:
                float(kv)
            except ValueError:
                only_numeric_in_rules = False
                break
    else:
        only_numeric_in_rules = False # nenhuma regra usa, aceita qualquer coisa
        
    if only_numeric_in_rules:
        if attribute in kb.attribute_ranges:
            limits = kb.attribute_ranges[attribute]
            if isinstance(limits, (list, tuple)) and len(limits) == 2:
                min_val = float(limits[0]) if limits[0] is not None else None
                max_val = float(limits[1]) if limits[1] is not None else None
                return None, False, format_range_message(min_val, max_val)
        return None, False, "espera-se um valor numérico"
        
    # Se não for restrito a números e não tiver comparações numéricas, aceitamos o texto livre
    return val_clean, True, ""


def format_range_message(min_val: Optional[float], max_val: Optional[float]) -> str:
    if min_val is not None and max_val is not None:
        min_str = int(min_val) if min_val.is_integer() else min_val
        max_str = int(max_val) if max_val.is_integer() else max_val
        return f"espera-se um valor numérico entre {min_str} e {max_str}"
    elif min_val is not None:
        min_str = int(min_val) if min_val.is_integer() else min_val
        return f"espera-se um valor numérico maior ou igual a {min_str}"
    elif max_val is not None:
        max_str = int(max_val) if max_val.is_integer() else max_val
        return f"espera-se um valor numérico menor ou igual a {max_str}"
    return "espera-se um valor numérico"




# ─── Estruturas de Dados ──────────────────────────────────────────────────────

@dataclass
class Fact:
    """Representa um fato na forma atributo=valor."""
    attribute: str
    value: Any
    source: str = "user"        # "user" | "inferred" | "initial"
    rule_id: Optional[str] = None  # regra que inferiu este fato
    cf: float = 1.0             # Certainty Factor (-1.0 to 1.0)

    def __eq__(self, other):
        if isinstance(other, Fact):
            return self.attribute == other.attribute and self.value == other.value
        return False

    def __hash__(self):
        return hash((self.attribute, str(self.value)))

    def __repr__(self):
        return f"{self.attribute} = {self.value}"


@dataclass
class Condition:
    """Condição de uma regra: atributo operador valor."""
    attribute: str
    operator: str   # "=", "!=", ">", "<", ">=", "<="
    value: Any

    def evaluate(self, facts: dict[str, Any]) -> bool:
        if self.attribute not in facts:
            return False
        fv = facts[self.attribute]
        cv = self.value
        try:
            fv_num = float(fv)
            cv_num = float(cv)
            ops = {
                "=": fv_num == cv_num, "!=": fv_num != cv_num,
                ">": fv_num > cv_num,  "<": fv_num < cv_num,
                ">=": fv_num >= cv_num, "<=": fv_num <= cv_num,
            }
        except (ValueError, TypeError):
            ops = {
                "=": str(fv).lower() == str(cv).lower(),
                "!=": str(fv).lower() != str(cv).lower(),
                ">": str(fv) > str(cv), "<": str(fv) < str(cv),
                ">=": str(fv) >= str(cv), "<=": str(fv) <= str(cv),
            }
        return ops.get(self.operator, False)

    def __repr__(self):
        return f"{self.attribute} {self.operator} {self.value}"


@dataclass
class Conclusion:
    """Conclusão de uma regra: atributo = valor."""
    attribute: str
    value: Any
    cf: float = 1.0

    def __repr__(self):
        return f"{self.attribute} = {self.value}"


@dataclass
class Rule:
    """Regra de produção: SE condições ENTÃO conclusão."""
    id: str
    name: str
    conditions: list[Condition]
    conclusion: Conclusion
    priority: int = 0
    description: str = ""
    condition_operator: str = "AND"
    cf: float = 1.0

    def is_applicable(self, facts: dict[str, Any]) -> bool:
        if not self.conditions:
            return True
        if self.condition_operator == "OR":
            return any(c.evaluate(facts) for c in self.conditions)
        return all(c.evaluate(facts) for c in self.conditions)

    def missing_conditions(self, facts: dict[str, Any]) -> list[Condition]:
        return [c for c in self.conditions if c.attribute not in facts]

    def failed_conditions(self, facts: dict[str, Any]) -> list[Condition]:
        return [c for c in self.conditions if not c.evaluate(facts)]

    def __repr__(self):
        op = f" {self.condition_operator} "
        conds = op.join(str(c) for c in self.conditions)
        return f"[{self.id}] SE {conds} ENTÃO {self.conclusion} (CF: {self.cf})"


# ─── Base de Conhecimento ─────────────────────────────────────────────────────

class KnowledgeBase:
    def __init__(self, domain: str = "generico", description: str = ""):
        self.domain = domain
        self.description = description
        self.rules: dict[str, Rule] = {}
        self.initial_facts: list[Fact] = []
        self.working_memory: dict[str, Fact] = {}    # fatos atuais da sessão
        self.inferred_facts: list[Fact] = []          # fatos inferidos nesta sessão
        self.hypotheses: list[str] = []               # lista de hipóteses/diagnósticos possíveis
        self.questions: dict[str, str] = {}           # atributo → pergunta ao usuário
        self.answer_options: dict[str, list] = {}     # atributo → opções válidas
        self.attribute_ranges: dict[str, list[float]] = {}  # atributo → [min, max]

    # ── Fatos ──────────────────────────────────────────────────────────────────

    def add_initial_fact(self, attribute: str, value: Any, cf: float = 1.0):
        f = Fact(attribute, value, source="initial", cf=cf)
        self.initial_facts.append(f)
        self.working_memory[attribute] = f

    def assert_fact(self, attribute: str, value: Any,
                    source: str = "user", rule_id: Optional[str] = None, cf: float = 1.0):
        f = Fact(attribute, value, source=source, rule_id=rule_id, cf=cf)
        self.working_memory[attribute] = f
        if source == "inferred":
            self.inferred_facts.append(f)

    def get_fact_value(self, attribute: str) -> Optional[Any]:
        f = self.working_memory.get(attribute)
        return f.value if f else None
        
    def get_fact(self, attribute: str) -> Optional[Fact]:
        return self.working_memory.get(attribute)

    def facts_dict(self) -> dict[str, Any]:
        return {attr: f.value for attr, f in self.working_memory.items()}

    def reset_session(self):
        self.working_memory = {}
        self.inferred_facts = []
        for f in self.initial_facts:
            self.working_memory[f.attribute] = f

    # ── Regras ─────────────────────────────────────────────────────────────────

    def add_rule(self, rule: Rule):
        self.rules[rule.id] = rule

    def remove_rule(self, rule_id: str) -> bool:
        if rule_id in self.rules:
            del self.rules[rule_id]
            return True
        return False

    def get_rules_sorted(self) -> list[Rule]:
        return sorted(self.rules.values(), key=lambda r: -r.priority)

    # ── Perguntas ──────────────────────────────────────────────────────────────

    def register_question(self, attribute: str, question: str,
                           options: Optional[list] = None):
        self.questions[attribute] = question
        if options:
            self.answer_options[attribute] = [str(o) for o in options]

    def register_attribute_range(self, attribute: str, min_val: Optional[float], max_val: Optional[float]):
        self.attribute_ranges[attribute] = [min_val, max_val]

    def remove_question(self, attribute: str) -> bool:
        removed = False
        if attribute in self.questions:
            del self.questions[attribute]
            removed = True
        if attribute in self.answer_options:
            del self.answer_options[attribute]
            removed = True
        if attribute in self.attribute_ranges:
            del self.attribute_ranges[attribute]
            removed = True
        return removed

    def register_hypothesis(self, attribute: str):
        if attribute not in self.hypotheses:
            self.hypotheses.append(attribute)

    # ── Persistência ───────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "description": self.description,
            "hypotheses": self.hypotheses,
            "initial_facts": [
                {"attribute": f.attribute, "value": f.value, "cf": f.cf} for f in self.initial_facts
            ],
            "rules": [
                {
                    "id": r.id,
                    "name": r.name,
                    "priority": r.priority,
                    "description": r.description,
                    "condition_operator": r.condition_operator,
                    "cf": r.cf,
                    "conditions": [
                        {"attribute": c.attribute, "operator": c.operator, "value": c.value}
                        for c in r.conditions
                    ],
                    "conclusion": {"attribute": r.conclusion.attribute, "value": r.conclusion.value, "cf": r.conclusion.cf},
                }
                for r in self.rules.values()
            ],
            "questions": self.questions,
            "answer_options": self.answer_options,
            "attribute_ranges": self.attribute_ranges,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeBase":
        kb = cls(domain=data.get("domain", "generico"),
                 description=data.get("description", ""))
        kb.hypotheses = data.get("hypotheses", [])
        kb.questions = data.get("questions", {})
        kb.answer_options = data.get("answer_options", {})
        kb.attribute_ranges = data.get("attribute_ranges", {})
        for fd in data.get("initial_facts", []):
            kb.add_initial_fact(fd["attribute"], fd["value"], cf=fd.get("cf", 1.0))
        for rd in data.get("rules", []):
            conditions = [
                Condition(c["attribute"], c["operator"], c["value"])
                for c in rd["conditions"]
            ]
            conc_data = rd["conclusion"]
            conclusion = Conclusion(conc_data["attribute"], conc_data["value"], cf=conc_data.get("cf", 1.0))
            rule = Rule(
                id=rd["id"],
                name=rd["name"],
                conditions=conditions,
                conclusion=conclusion,
                priority=rd.get("priority", 0),
                description=rd.get("description", ""),
                condition_operator=rd.get("condition_operator", "AND"),
                cf=rd.get("cf", 1.0)
            )
            kb.add_rule(rule)
        return kb

    def save(self, path: str):
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str) -> "KnowledgeBase":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
