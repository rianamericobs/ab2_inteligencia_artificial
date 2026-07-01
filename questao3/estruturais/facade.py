from sistemaEvento import SistemaEventos
from comportamentais.observer import NotificacaoObservador
from tratar.excessoes import *


class SistemaFacade:
    def __init__(self):
        self._sistema = SistemaEventos()
        self._sistema.facade = self  # Para que a classe tenha referencia a ela mesma
        self._configurarServicos()

    def _configurarServicos(self):
        notificacaoServico = NotificacaoObservador(self._sistema.notificacoes_ref)
        self._sistema.anexar(notificacaoServico)

    # O único método que o "evento" precisará chamar
    def iniciarAplicacao(self):
        print(
            "Facade: A iniciar a execução da aplicação através do sistema de estados..."
        )
        self._sistema.ExecutarEstado()

    # === Métodos do menu principal
    def criar_evento(self):
        self._sistema.criar_evento()

    def analisar_feedbacks_com_llm(self):
        self._sistema.analisar_feedbacks_com_llm()

    def executar_agente_feedback(self):
        self._sistema.executar_agente_feedback()

    def cancelar_evento(self):

        self._sistema.cancelar_evento()

    def listar_eventos(self):
        self._sistema.listar_eventos()

    def criar_survey_evento(self):
        self._sistema.criar_survey_evento()

    def coletar_feedback_evento(self):
        self._sistema.coletar_feedback_evento()

    def listar_feedbacks_evento(self):
        self._sistema.listar_feedbacks_evento()

    def adicionar_speaker_evento(self):
        self._sistema.adicionar_speaker_evento()

    def listar_speakers_evento(self):
        self._sistema.listar_speakers_evento()

    def remover_speaker_evento(self):
        self._sistema.remover_speaker_evento()

    def reservar_local_evento(self):
        self._sistema.reservar_local_evento()

    # ----- Gerenciar participante

    def adicionar_participante_evento(self):
        self._sistema.adicionar_participante_evento()

    def listar_participantes_evento(self):
        self._sistema.listar_participantes_evento()

    def excluir_participante_evento(self):
        self._sistema.excluir_participante_evento()

    # --- Gerenciar Fornecedor

    def adicionar_fornecedor_evento(self):
        self._sistema.adicionar_fornecedor_evento()

    def listar_fornecedores_evento(self):
        self._sistema.listar_fornecedores_evento()

    def atualizar_status_fornecedor_evento(self):
        self._sistema.atualizar_status_fornecedor_evento()

    # --- Financeiro

    def definir_orcamento_evento(self):
        self._sistema.definir_orcamento_evento()

    def registrar_despesa_evento(self):
        self._sistema.registrar_despesa_evento()

    def ver_financas_evento(self):
        self._sistema.ver_financas_evento()

    def remover_despesa_evento(self):
        self._sistema.remover_despesa_evento()

    # --- Locais

    def adicionar_local(self):
        self._sistema.adicionar_local()

    def listar_locais_disponiveis(self):
        self._sistema.listar_locais_disponiveis()

    def remover_local(self):
        self._sistema.remover_local()

    def gerar_relatorio_completo_evento(self):
        print("\n--- Relatório Completo do Evento (via Facade) ---")
        evento_selecionado = self._sistema.selecionar_evento()
        if evento_selecionado:
            print("\n** Detalhes Financeiros **")
            self._sistema.ver_financas_evento()

            print("\n** Lista de Participantes **")
            self._sistema.listar_participantes_evento()

            print("\n** Lista de Palestrantes **")
            self._sistema.listar_speakers_evento()

            print("\n** Listar localidades **")
            self._sistema.listar_locais_disponiveis()

            print("\n** Listar Feedbacks **")
            self._sistema.listar_feedbacks_evento()

            print("\n** Lista de fornecedores **")
            self._sistema.listar_fornecedores_evento()

    def importar_locais_de_csv(self):
        self._sistema.importar_locais_de_csv()

    def importar_participantes_csv(self):
        self._sistema.importar_participantes_csv()

    def importar_fornecedor_csv(self):
        self._sistema.importar_fornecedor_csv()
