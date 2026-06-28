"""
Módulo: Interface de Linha de Comando (CLI Shell)
Interface principal para interação com o sistema especialista.
"""
from __future__ import annotations
import os
import sys
from typing import Optional

# Ajuste de path para importações relativas quando executado diretamente
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.knowledge_base import KnowledgeBase, normalize_option, is_numeric_attribute, validate_free_input, Rule, Condition, Conclusion
from core.inference_engine import InferenceEngine
from core.explanation import ExplanationEngine
from core.kb_editor import KBEditor
from core.llm_client import GroqClient

BANNER = r"""
╔══════════════════════════════════════════════════════════════╗
║          K-RuleShell — Sistema Baseado em Conhecimento       ║
║         Shell Genérica para Diagnóstico e Recomendação       ║
╚══════════════════════════════════════════════════════════════╝
"""

HELP_MAIN = """
COMANDOS DISPONÍVEIS:
  carregar <arquivo.json>   Carrega uma base de conhecimento
  salvar   <arquivo.json>   Salva a base de conhecimento atual
  nova                      Cria uma nova base de conhecimento
  consulta                  Inicia uma consulta diagnóstica (modo híbrido)
  forward                   Executa encadeamento para frente
  backward <hipotese>       Executa encadeamento para trás sobre uma hipótese
  fatos                     Exibe fatos da sessão atual
  regras                    Lista todas as regras
  adicionar regra           Cadastra nova regra interativamente
  remover regra <id>        Remove uma regra
  editar regra <id>         Edita uma regra existente
  adicionar fato            Adiciona fato inicial
  adicionar pergunta        Cadastra pergunta para um atributo
  adicionar hipotese        Cadastra atributo como hipótese alvo
  ia                        Menu do assistente de IA (regras e perguntas)
  ia regra                  Cadastra regra(s) usando linguagem natural (IA)
  ia pergunta               Cadastra pergunta(s) usando linguagem natural (IA)
  porque <atributo>         Explica por que um atributo foi perguntado
  como <atributo>           Explica como uma conclusão foi obtida
  trilha                    Exibe trilha completa de inferência
  resumo                    Resumo da sessão atual
  resetar                   Reinicia a sessão (mantém a KB)
  info                      Informações sobre a base de conhecimento
  ajuda                     Exibe esta ajuda
  sair                      Encerra o programa
"""


class CLIShell:
    def __init__(self, kb: Optional[KnowledgeBase] = None):
        self.kb = kb or KnowledgeBase(domain="generico")
        self.llm = GroqClient()
        self._rebuild_components()
        self._last_question_attr: Optional[str] = None

    def _rebuild_components(self):
        self.engine = InferenceEngine(self.kb, ask_user_callback=self._ask_user_callback)
        self.explanation = ExplanationEngine(self.kb, self.engine)
        self.editor = KBEditor(self.kb)

    def _ask_user_callback(self, attribute: str, question: str,
                            options: list) -> Optional[str]:
        """Callback chamado pelo motor para perguntar ao usuário com loop de validação e IA."""
        self._last_question_attr = attribute
        print(f"\n{question}")
        
        while True:
            if options:
                print(f"   Opções: {', '.join(options)}")
            answer = input("   Resposta: ").strip()
            if not answer:
                return None
            
            # Verificar comandos globais/explicação
            cmd_lower = answer.lower()
            if cmd_lower.startswith("porque"):
                parts = answer.split(maxsplit=1)
                attr = parts[1] if len(parts) > 1 else attribute
                why_text = self.explanation.why(attr)
                if self.llm and self.llm.is_available():
                    print(self.llm.explain_natural_language(why_text))
                else:
                    print(why_text)
                continue
            elif cmd_lower == "resumo":
                print(self.explanation.session_summary())
                continue
            elif cmd_lower == "fatos":
                self.editor.list_facts()
                continue
            elif cmd_lower == "regras":
                self.editor.list_rules()
                continue
            elif cmd_lower in ("ajuda", "help", "?"):
                print("\nComandos disponíveis durante a pergunta:")
                print("  porque              Explica por que este atributo está sendo perguntado")
                print("  porque <atributo>   Explica por que outro atributo foi perguntado")
                print("  resumo              Exibe o resumo da sessão atual")
                print("  fatos               Exibe os fatos conhecidos até agora")
                print("  regras              Lista as regras da base")
                print("  sair                Aborta a consulta atual")
                continue
            elif cmd_lower in ("sair", "exit", "quit"):
                print("Consulta abortada.")
                return None
                
            if options:
                # 1. Normalização determinística local
                normalized = normalize_option(answer, options)
                if normalized:
                    return normalized
                
                # 2. IA para interpretar linguagem natural
                if self.llm and self.llm.is_available():
                    mapped = self.llm.map_answer_to_options(question, options, answer)
                    if mapped and mapped in options:
                        print(f"   [IA] Mapeado '{answer}' para '{mapped}'")
                        return mapped
                
                print(f"   Aviso: Valor '{answer}' não é válido. Por favor, escolha uma das opções.")
            else:
                val_normalized, is_valid, err_msg = validate_free_input(self.kb, attribute, answer)
                if is_valid:
                    return val_normalized
                else:
                    print(f"   Aviso: O valor '{answer}' não é válido para o atributo '{attribute}' ({err_msg}).")

    # ── Loop principal ────────────────────────────────────────────────────────

    def run(self):
        print(BANNER)
        print("Digite 'ajuda' para ver os comandos disponíveis.")
        if self.kb.domain != "generico":
            print(f"Base de conhecimento carregada: '{self.kb.domain}'")

        while True:
            try:
                raw = input(f"\n[{self.kb.domain}] > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nEncerrando KBS-Shell. Até logo!")
                break

            if not raw:
                continue

            cmd = raw.lower()
            parts = raw.split(maxsplit=2)
            cmd0 = parts[0].lower()
            cmd1 = parts[1].lower() if len(parts) > 1 else ""
            arg = parts[2] if len(parts) > 2 else (parts[1] if len(parts) > 1 else "")

            # ── Comandos ──────────────────────────────────────────────────────

            if cmd in ("sair", "exit", "quit"):
                print("Encerrando KBS-Shell. Até logo!")
                break

            elif cmd in ("ajuda", "help", "?"):
                print(HELP_MAIN)

            elif cmd0 == "carregar":
                path = arg or cmd1
                if not path:
                    path = input("Caminho do arquivo: ").strip()
                self._load_kb(path)

            elif cmd0 == "salvar":
                path = arg or cmd1
                if not path:
                    path = input("Caminho do arquivo: ").strip()
                self.editor.save(path)

            elif cmd == "nova":
                self._new_kb()

            elif cmd == "consulta":
                self._run_consultation()

            elif cmd == "forward":
                self._run_forward()

            elif cmd0 == "backward":
                hyp = arg or cmd1
                if not hyp:
                    hyp = input("Hipótese/atributo alvo: ").strip()
                self._run_backward(hyp)

            elif cmd == "fatos":
                self.explanation.session_summary()
                self.editor.list_facts()

            elif cmd == "regras":
                self.editor.list_rules()

            elif cmd0 == "adicionar" and cmd1 == "regra":
                self.editor.add_rule_interactive()

            elif cmd0 == "remover" and cmd1 == "regra":
                rule_id = arg if arg else input("ID da regra: ").strip()
                self.editor.remove_rule(rule_id)

            elif cmd0 == "editar" and cmd1 == "regra":
                rule_id = arg if arg else input("ID da regra: ").strip()
                self.editor.edit_rule(rule_id)

            elif cmd0 == "adicionar" and cmd1 == "fato":
                self.editor.add_initial_fact_interactive(self.llm)

            elif cmd0 == "adicionar" and cmd1 == "pergunta":
                self.editor.add_question_interactive()

            elif cmd0 == "adicionar" and cmd1 == "hipotese":
                self.editor.add_hypothesis_interactive()

            elif cmd0 == "ia" and cmd1 == "regra":
                self._ia_menu("regra")

            elif cmd0 == "ia" and cmd1 == "pergunta":
                self._ia_menu("pergunta")

            elif cmd == "ia":
                self._ia_menu()

            elif cmd0 in ("porque", "por", "why"):
                attr = arg or cmd1
                if not attr:
                    attr = input("Atributo: ").strip()
                why_text = self.explanation.why(attr)
                if self.llm and self.llm.is_available():
                    print(self.llm.explain_natural_language(why_text))
                else:
                    print(why_text)

            elif cmd0 in ("como", "how"):
                attr = arg or cmd1
                if not attr:
                    attr = input("Atributo: ").strip()
                how_text = self.explanation.how(attr)
                if self.llm and self.llm.is_available():
                    print(self.llm.explain_natural_language(how_text))
                else:
                    print(how_text)

            elif cmd == "trilha":
                print(self.explanation.full_trace())

            elif cmd == "resumo":
                print(self.explanation.session_summary())

            elif cmd == "resetar":
                self.engine.reset()
                print(" Sessão reiniciada. Fatos iniciais restaurados.")

            elif cmd == "info":
                self._show_info()

            else:
                print(f"Comando não reconhecido: '{raw}'. Digite 'ajuda' para ver os comandos.")

    # ── Fluxos de consulta ────────────────────────────────────────────────────

    def _run_consultation(self):
        """Modo de consulta completa com estratégia híbrida."""
        print("\n" + "═" * 60)
        print(f"  CONSULTA DIAGNÓSTICA — {self.kb.domain.upper()}")
        print("═" * 60)
        print("Durante a consulta, você pode digitar:")
        print("  'porque <atributo>'  para entender por que a pergunta foi feita")
        print("  'resumo'             para ver os fatos coletados até agora")
        print()

        if not self.kb.rules:
            print("Nenhuma regra cadastrada na base de conhecimento.")
            return

        self.engine.reset()
        results = self.engine.hybrid_chain(self.kb.hypotheses)

        print("\n" + "═" * 60)
        print("  RESULTADO DO DIAGNÓSTICO")
        print("═" * 60)

        if not results:
            print("Não foi possível chegar a um diagnóstico com as informações fornecidas.")
        else:
            has_conclusion = False
            concluded_hypotheses = [hyp for hyp, values in results.items() if values]
            for hyp, values in results.items():
                if values:
                    has_conclusion = True
                    for v in values:
                        print(f"\n  {hyp}: {v}")
                        # Mostrar recomendações associadas
                        recs = self._get_recommendations(hyp, v, concluded_hypotheses)
                        if recs:
                            print(f"\n  Recomendações:")
                            for rec in recs:
                                print(f"     • {rec}")
            if not has_conclusion:
                print("  Não foi possível confirmar nenhum diagnóstico.")

        # Mostrar trilha resumida
        if self.engine.trace.steps:
            print(f"\n  Inferências realizadas: {len(self.engine.trace.steps)} passo(s)")
            print("  Digite 'trilha' para ver a cadeia completa.")
            print("  Digite 'como <atributo>' para explicar uma conclusão específica.")

    def _run_forward(self):
        print("\nExecutando Encadeamento para Frente...")
        self.engine.reset()
        conclusions = self.engine.forward_chain()
        if conclusions:
            print(f"  Conclusões inferidas ({len(conclusions)}):")
            for c in conclusions:
                print(f"  ✓ {c}")
        else:
            print("  Nenhuma nova conclusão inferida com os fatos atuais.")

    def _run_backward(self, goal: str):
        print(f"\nExecutando Encadeamento para Trás — objetivo: '{goal}'")
        self.engine.reset()
        proved = self.engine.backward_chain(goal)
        val = self.kb.get_fact_value(goal)
        if proved or val is not None:
            print(f"  Objetivo provado: {goal} = {val}")
        else:
            print(f" Não foi possível provar o objetivo '{goal}'.")

    def _get_recommendations(self, attribute: str, value: str, concluded_hypotheses: list[str]) -> list[str]:
        """Coleta recomendações a partir de fatos inferidos associados ao diagnóstico."""
        recs = []
        # Buscar na memória de trabalho fatos do tipo "recomendacao_*" ou "tratamento_*"
        for attr, fact in self.kb.working_memory.items():
            if attr in concluded_hypotheses:
                continue
            if "recomendacao" in attr.lower() or "tratamento" in attr.lower() or "conduta" in attr.lower():
                if attr.lower() != attribute.lower():
                    recs.append(f"{attr}: {fact.value}")
        return recs

    # ── Auxiliares ────────────────────────────────────────────────────────────

    def _load_kb(self, path: str):
        try:
            self.kb = KnowledgeBase.load(path)
            self._rebuild_components()
            print(f" Base '{self.kb.domain}' carregada — {len(self.kb.rules)} regra(s), "
                  f"{len(self.kb.hypotheses)} hipótese(s).")
        except FileNotFoundError:
            print(f"Arquivo não encontrado: '{path}'")
        except Exception as e:
            print(f"Erro ao carregar: {e}")

    def _new_kb(self):
        domain = input("Nome do domínio: ").strip()
        description = input("Descrição: ").strip()
        self.kb = KnowledgeBase(domain=domain, description=description)
        self._rebuild_components()
        print(f" Nova base de conhecimento criada para o domínio '{domain}'.")

    def _show_info(self):
        print(f"\n{'─'*60}")
        print(f"  INFORMAÇÕES DA BASE DE CONHECIMENTO")
        print(f"{'─'*60}")
        print(f"  Domínio:    {self.kb.domain}")
        print(f"  Descrição:  {self.kb.description or '(não definida)'}")
        print(f"  Regras:     {len(self.kb.rules)}")
        print(f"  Fatos iniciais: {len(self.kb.initial_facts)}")
        print(f"  Hipóteses:  {self.kb.hypotheses or '(não definidas)'}")
        print(f"  Perguntas cadastradas: {list(self.kb.questions.keys())}")

    def _ia_menu(self, mode: Optional[str] = None):
        """Comando centralizado de IA para regras e perguntas."""
        if not self.llm or not self.llm.is_available():
            print("Aviso: A funcionalidade de IA não está disponível (verifique a API_KEY).")
            return

        # Se não especificou o modo, exibir o menu interativo
        if not mode:
            print("\n──── ASSISTENTE IA DA BASE DE CONHECIMENTO ────")
            print("Escolha o que a IA deve ajudar a cadastrar:")
            print("  1. Adicionar regra(s)")
            print("  2. Adicionar pergunta(s)")
            opcao = input("Opção (1 ou 2, ou Enter para sair): ").strip()
            if opcao == "1":
                mode = "regra"
            elif opcao == "2":
                mode = "pergunta"
            else:
                return

        # Modo de regras
        if mode in ("regra", "regras"):
            self._add_rules_ia_flow()
        # Modo de perguntas
        elif mode in ("pergunta", "perguntas"):
            self._add_questions_ia_flow()
        else:
            print("Opção inválida.")

    def _add_rules_ia_flow(self):
        print("\n──── CADASTRAR REGRAS COM IA ────")
        text = input("Descreva a(s) regra(s) em linguagem natural (pode descrever várias de uma vez):\n> ").strip()
        if not text:
            return

        kb_rules = []
        for r in self.kb.rules.values():
            kb_rules.append(f"- [{r.id}] {r.name}: SE {r.conditions} ENTÃO {r.conclusion}")
            
        current_kb_info = f"""
Domínio: {self.kb.domain}
Descrição: {self.kb.description}
Perguntas/Opções registradas: {self.kb.answer_options}
Hipóteses: {self.kb.hypotheses}
Regras cadastradas atualmente:
{chr(10).join(kb_rules)}
"""
        print("\nProcessando com a IA...")
        rules_list = self.llm.parse_rules_from_natural_language(text, current_kb_info)
        
        if not rules_list:
            print("Não foi possível gerar regras estruturadas a partir da descrição fornecida.")
            return

        print(f"\nRegras geradas pela IA ({len(rules_list)}):")
        for i, rule_data in enumerate(rules_list):
            print(f"\n[{i+1}] Regra estruturada:")
            print(f"  ID:          {rule_data.get('id')}")
            print(f"  Nome:        {rule_data.get('name')}")
            print(f"  Descrição:   {rule_data.get('description', '')}")
            print(f"  Prioridade:  {rule_data.get('priority', 0)}")
            print("  SE:")
            for cond in rule_data.get('conditions', []):
                print(f"    • {cond.get('attribute')} {cond.get('operator')} {cond.get('value')}")
            conc = rule_data.get('conclusion', {})
            print(f"  ENTÃO:\n    • {conc.get('attribute')} = {conc.get('value')}")

        confirm = input("\nDeseja salvar essa(s) regra(s) na base de conhecimento? (sim/nao): ").strip().lower()
        if confirm in ("sim", "s"):
            added_count = 0
            for rule_data in rules_list:
                try:
                    conditions = [
                        Condition(c["attribute"], c["operator"], c["value"])
                        for c in rule_data["conditions"]
                    ]
                    conclusion = Conclusion(rule_data["conclusion"]["attribute"], rule_data["conclusion"]["value"])
                    rule = Rule(
                        id=rule_data["id"],
                        name=rule_data["name"],
                        conditions=conditions,
                        conclusion=conclusion,
                        priority=rule_data.get("priority", 0),
                        description=rule_data.get("description", "")
                    )
                    self.kb.add_rule(rule)
                    added_count += 1
                except Exception as e:
                    print(f"Erro ao salvar a regra {rule_data.get('id')}: {e}")
            print(f"Sucesso! {added_count} regra(s) cadastrada(s) com sucesso.")
        else:
            print("Operação cancelada.")

    def _add_questions_ia_flow(self):
        print("\n──── CADASTRAR PERGUNTAS COM IA ────")
        text = input("Descreva a(s) pergunta(s) em linguagem natural (pode descrever várias de uma vez):\n> ").strip()
        if not text:
            return

        current_kb_info = f"""
Domínio: {self.kb.domain}
Descrição: {self.kb.description}
Perguntas/Opções registradas atualmente: {self.kb.answer_options}
Limites numéricos atuais: {self.kb.attribute_ranges}
Hipóteses: {self.kb.hypotheses}
"""
        print("\nProcessando com a IA...")
        questions_list = self.llm.parse_questions_from_natural_language(text, current_kb_info)
        
        if not questions_list:
            print("Não foi possível gerar perguntas estruturadas a partir da descrição fornecida.")
            return

        print(f"\nPerguntas geradas pela IA ({len(questions_list)}):")
        for i, q_data in enumerate(questions_list):
            print(f"\n[{i+1}] Pergunta estruturada:")
            print(f"  Atributo:    {q_data.get('attribute')}")
            print(f"  Pergunta:    {q_data.get('question')}")
            if q_data.get('options'):
                print(f"  Opções:      {', '.join(q_data.get('options'))}")
            else:
                print("  Opções:      (resposta livre)")
            if q_data.get('range'):
                print(f"  Limites:     min={q_data.get('range')[0]}, max={q_data.get('range')[1]}")

        confirm = input("\nDeseja salvar essa(s) pergunta(s) na base de conhecimento? (sim/nao): ").strip().lower()
        if confirm in ("sim", "s"):
            added_count = 0
            for q_data in questions_list:
                try:
                    attr = q_data["attribute"]
                    self.kb.register_question(attr, q_data["question"], q_data.get("options"))
                    
                    rng = q_data.get("range")
                    if rng and isinstance(rng, list) and len(rng) == 2:
                        min_val = float(rng[0]) if rng[0] is not None else None
                        max_val = float(rng[1]) if rng[1] is not None else None
                        if min_val is not None or max_val is not None:
                            self.kb.register_attribute_range(attr, min_val, max_val)
                            
                    added_count += 1
                except Exception as e:
                    print(f"Erro ao salvar a pergunta para '{q_data.get('attribute')}': {e}")
            print(f"Sucesso! {added_count} pergunta(s) cadastrada(s) com sucesso.")
        else:
            print("Operação cancelada.")
