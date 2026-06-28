"""
Módulo: Editor da Base de Conhecimento
Permite criar, editar, remover regras e fatos via terminal.
"""
from __future__ import annotations
import os
from .knowledge_base import KnowledgeBase, Rule, Condition, Conclusion, Fact, normalize_option, is_numeric_attribute, validate_free_input


OPERATORS = ["=", "!=", ">", "<", ">=", "<="]


class KBEditor:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb

    # ── Regras ────────────────────────────────────────────────────────────────

    def add_rule_interactive(self):
        """Interface interativa para cadastro de uma nova regra."""
        print("\n──── NOVA REGRA ────")
        rule_id = input("ID da regra (ex: R1): ").strip()
        if rule_id in self.kb.rules:
            print(f"Regra '{rule_id}' já existe. Use 'editar regra' para modificá-la.")
            return
        name = input("Nome/descrição curta: ").strip()
        description = input("Descrição detalhada (opcional): ").strip()
        priority = input("Prioridade (0=padrão, maior=primeiro): ").strip()
        priority = int(priority) if priority.isdigit() else 0
        
        op_rule = input("Conectivo das condições E (AND) ou OU (OR) [padrão E]: ").strip().upper()
        condition_operator = "OR" if op_rule in ("OU", "OR") else "AND"
        
        cf_rule_str = input("Fator de Certeza da Regra (CF 0.0 a 1.0) [padrão 1.0]: ").strip()
        try:
            cf_rule = float(cf_rule_str.replace(",", ".")) if cf_rule_str else 1.0
        except ValueError:
            cf_rule = 1.0

        conditions = []
        op_label = "OU" if condition_operator == "OR" else "E"
        print(f"\nCondições (SE ... {op_label} ...). Digite vazio para finalizar.")
        while True:
            attr = input("  Atributo: ").strip()
            if not attr:
                break
            op = input(f"  Operador {OPERATORS}: ").strip()
            if op not in OPERATORS:
                print(f"  Operador inválido. Use um de {OPERATORS}")
                continue
            val = input("  Valor: ").strip()
            conditions.append(Condition(attr, op, val))
            print(f"  ✓ Condição adicionada: {attr} {op} {val}")

        if not conditions:
            print("Nenhuma condição definida. Regra não cadastrada.")
            return

        print("\nConclusão (ENTÃO ...):")
        c_attr = input("  Atributo: ").strip()
        c_val = input("  Valor: ").strip()

        rule = Rule(
            id=rule_id, name=name, conditions=conditions,
            conclusion=Conclusion(c_attr, c_val, cf=1.0),
            priority=priority, description=description,
            condition_operator=condition_operator, cf=cf_rule
        )
        self.kb.add_rule(rule)
        print(f"\nRegra '{rule_id}' cadastrada: {rule}")

    def add_rule_programmatic(self, rule_id: str, name: str,
                               conditions: list[tuple], conclusion: tuple,
                               priority: int = 0, description: str = "") -> Rule:
        """Adiciona regra programaticamente. conditions: [(attr, op, val), ...]"""
        conds = [Condition(a, o, v) for a, o, v in conditions]
        conc = Conclusion(conclusion[0], conclusion[1])
        rule = Rule(id=rule_id, name=name, conditions=conds, conclusion=conc,
                    priority=priority, description=description)
        self.kb.add_rule(rule)
        return rule

    def edit_rule(self, rule_id: str):
        """Edita uma regra existente (recria interativamente)."""
        if rule_id not in self.kb.rules:
            print(f"Regra '{rule_id}' não encontrada.")
            return
        print(f"Editando regra '{rule_id}'. A regra atual será substituída.")
        print(f"  Atual: {self.kb.rules[rule_id]}")
        self.kb.remove_rule(rule_id)
        self.add_rule_interactive()

    def remove_rule(self, rule_id: str):
        if self.kb.remove_rule(rule_id):
            print(f"Regra '{rule_id}' removida.")
        else:
            print(f"Regra '{rule_id}' não encontrada.")

    def list_rules(self):
        if not self.kb.rules:
            print("Base de conhecimento sem regras.")
            return
        print(f"\n{'─'*60}")
        print(f"REGRAS DA BASE DE CONHECIMENTO — {self.kb.domain.upper()}")
        print(f"{'─'*60}")
        for r in self.kb.get_rules_sorted():
            print(f"\n  [{r.id}] {r.name}  (prioridade: {r.priority}, CF: {r.cf:.2f})")
            if r.description:
                print(f"       {r.description}")
            op = f" {r.condition_operator}\n           "
            conds = op.join(str(c) for c in r.conditions)
            print(f"  SE  {conds}")
            print(f"  ENTÃO  {r.conclusion}")
        print(f"\nTotal: {len(self.kb.rules)} regra(s)\n")

    # ── Fatos Iniciais ────────────────────────────────────────────────────────

    def add_initial_fact_interactive(self, llm_client=None):
        attr = input("Atributo: ").strip()
        if not attr:
            return
        options = self.kb.answer_options.get(attr)
        cf_fact_str = input("Fator de Certeza do Fato (CF 0.0 a 1.0) [padrão 1.0]: ").strip()
        try:
            cf_fact = float(cf_fact_str.replace(",", ".")) if cf_fact_str else 1.0
        except ValueError:
            cf_fact = 1.0

        while True:
            if options:
                print(f"Opções para '{attr}': {', '.join(options)}")
                val = input("Valor: ").strip()
                if not val:
                    return
                if options:
                    normalized = normalize_option(val, options)
                    if normalized:
                        self.kb.add_initial_fact(attr, normalized, cf=cf_fact)
                        print(f"Fato inicial adicionado: {attr} = {normalized} (CF: {cf_fact:.2f})")
                        break
                    if llm_client and llm_client.is_available():
                        question = self.kb.questions.get(attr, f"Qual o valor de {attr}?")
                        mapped = llm_client.map_answer_to_options(question, options, val)
                        if mapped and mapped in options:
                            print(f"[IA] Mapeado '{val}' para '{mapped}'")
                            self.kb.add_initial_fact(attr, mapped, cf=cf_fact)
                            print(f"Fato inicial adicionado: {attr} = {mapped} (CF: {cf_fact:.2f})")
                            break
                    print(f"Aviso: Valor '{val}' não é válido para o atributo '{attr}'.")
            else:
                val = input("Valor: ").strip()
                if not val:
                    return
                val_normalized, is_valid, err_msg = validate_free_input(self.kb, attr, val)
                if is_valid:
                    self.kb.add_initial_fact(attr, val_normalized, cf=cf_fact)
                    print(f"Fato inicial adicionado: {attr} = {val_normalized} (CF: {cf_fact:.2f})")
                    break
                else:
                    print(f"Aviso: O valor '{val}' não é válido para o atributo '{attr}' ({err_msg}).")

    def list_facts(self):
        if not self.kb.working_memory:
            print("Nenhum fato na memória de trabalho.")
            return
        print("\nFATOS ATUAIS:")
        for attr, f in self.kb.working_memory.items():
            print(f"  {attr} = {f.value} (CF: {f.cf:.2f})  [{f.source}]")

    # ── Perguntas ─────────────────────────────────────────────────────────────

    def add_question_interactive(self):
        attr = input("Atributo: ").strip()
        if not attr:
            return
        question = input("Pergunta ao usuário: ").strip()
        opts_raw = input("Opções de resposta (separadas por vírgula, ou Enter para livre): ").strip()
        options = [o.strip() for o in opts_raw.split(",")] if opts_raw else None
        self.kb.register_question(attr, question, options)
        
        # Se for resposta livre, oferecer o cadastro de limites numéricos
        if not options:
            define_limits = input("Deseja definir limites numéricos (mínimo/máximo) para este atributo? (s/n): ").strip().lower()
            if define_limits in ("s", "sim", "y", "yes"):
                min_val_str = input("  Valor mínimo (deixe em branco se não houver): ").strip()
                max_val_str = input("  Valor máximo (deixe em branco se não houver): ").strip()
                
                min_val = None
                if min_val_str:
                    try:
                        min_val = float(min_val_str.replace(",", "."))
                    except ValueError:
                        print("  Aviso: Mínimo inválido. Ignorado.")
                        
                max_val = None
                if max_val_str:
                    try:
                        max_val = float(max_val_str.replace(",", "."))
                    except ValueError:
                        print("  Aviso: Máximo inválido. Ignorado.")
                
                if min_val is not None or max_val is not None:
                    self.kb.register_attribute_range(attr, min_val, max_val)
                    print(f"  ✓ Limites registrados para '{attr}': min={min_val}, max={max_val}")
                    
        print(f"Pergunta registrada para '{attr}'.")

    def add_hypothesis_interactive(self):
        attr = input("Nome do atributo de hipótese: ").strip()
        if not attr:
            return
        self.kb.register_hypothesis(attr)
        print(f"Hipótese '{attr}' registrada.")

    # ── Persistência ─────────────────────────────────────────────────────────

    def save(self, path: str):
        self.kb.save(path)
        print(f"Base de conhecimento salva em: {path}")

    def load(self, path: str) -> KnowledgeBase:
        kb = KnowledgeBase.load(path)
        self.kb = kb
        print(f"Base carregada: domínio '{kb.domain}' com {len(kb.rules)} regra(s).")
        return kb
