from abc import ABC, abstractmethod
from .command import *


class MaquinaEstados(ABC):
    def __init__(self, sistema):
        self.sistema = sistema

    @abstractmethod
    def run(self):
        pass

    def display_menu(self, opcoes):
        # mostrar os estados
        for chave, valor in opcoes.items():
            if chave != "0":
                print(f"{chave}. {valor}")
        print("0. Voltar")

    def __str__(self):
        return self.__class__.__name__


# --- Estado do Menu Principal ---


class MenuPrincipalState(MaquinaEstados):
    def run(self):
        opcoes = {
            "1": "Gerir Evento",
            "2": "Gerir Participante",
            "3": "Gerir Fornecedores",
            "4": "Gerir Finanças",
            "5": "Gerir Locais",
            "6": "Gerar Relatório Completo de um Evento",
        }
        comandoExtra = {"6": GerarRelatorioGeralCommand(self.sistema.facade)}

        while True:
            print("\n====== MENU PRINCIPAL ======")
            self.display_menu(opcoes)
            op = input("Opção: ")

            if op == "1":
                # Transição para o estado de gestão de eventos
                self.sistema.set_state(GestaoEventoState(self.sistema))
                break
            elif op == "2":
                self.sistema.set_state(GestaoParticipanteState(self.sistema))
                break
            elif op == "3":
                self.sistema.set_state(GestaoFornecedoresState(self.sistema))
                break
            elif op == "4":
                self.sistema.set_state(GestaoFinancasState(self.sistema))
                break
            elif op == "5":
                self.sistema.set_state(GestaoLocaisState(self.sistema))
                break
            elif op == "6":
                comando = comandoExtra.get(op)
                if comando:
                    comando.executar()

            elif op == "0":
                self.sistema.set_state(None)  # Sinaliza o fim da aplicação
                break
            else:
                print("Opção inválida.")


# --- Estado de Gestão de Eventos ---
class GestaoEventoState(MaquinaEstados):
    def run(self):
        comandos = {
            "1": CriarEventoCommand(self.sistema),
            "2": CancelarEventoCommand(self.sistema),
            "3": ListarEventoCommand(self.sistema),
            "4": CriarSurveyEventoCommand(self.sistema),
            "5": ColetarFeedbackEventoCommand(self.sistema),
            "6": ListarFeedbacksEventoCommand(self.sistema),
            "7": AdicionarSpeakerEventoCommand(self.sistema),
            "8": ListarSpeakersEventoCommand(self.sistema),
            "9": RemoverSpeakerEventoCommand(self.sistema),
            "10": ReservarLocalEventoCommand(self.sistema),
            "11": AnalisarFeedbackLLMCommand(self.sistema),
            "12": ExecutarAgenteFeedbackLLMCommand(self.sistema),
        }

        opcoes = {
            "1": "Criar evento",
            "2": "Cancelar evento",
            "3": "Listar eventos",
            "4": "Criar pesquisa",
            "5": "Coletar feedback",
            "6": "Listar feedbacks",
            "7": "Adicionar palestrante",
            "8": "Listar palestrantes",
            "9": "Remover palestrante",
            "10": "Reservar local",
            "11": "Analisar feedback com IA",
            "12": "Executar agente de melhoria com IA",
        }

        while True:
            print("\n--- GERIR EVENTO ---")
            self.display_menu(opcoes)
            op = input("Opção: ")

            if op == "0":
                # Transição de volta para o menu principal
                self.sistema.set_state(MenuPrincipalState(self.sistema))
                break

            comando = comandos.get(op)
            if comando:
                comando.executar()
            else:
                print("Inválido.")


# --- Estado de Gestão de Participantes ---
class GestaoParticipanteState(MaquinaEstados):
    def run(self):
        comandos = {
            "1": AdicionarParticipanteEventoCommand(self.sistema),
            "2": ListarParticipanteEventoCommand(self.sistema),
            "3": ExcluirParticipanteEventoCommand(self.sistema),
            "4": ImportarParticipanteCsvCommand(self.sistema),
        }
        opcoes = {
            "1": "Adicionar Participante",
            "2": "Listar Participantes",
            "3": "Excluir participantes",
            "4": "Importar participantes csv",
        }

        while True:
            print("\n--- GERIR PARTICIPANTE ---")
            self.display_menu(opcoes)
            op = input("Opção: ")

            if op == "0":
                self.sistema.set_state(MenuPrincipalState(self.sistema))
                break

            comando = comandos.get(op)
            if comando:
                comando.executar()
            else:
                print("Opção Inválida.")


class GestaoFornecedoresState(MaquinaEstados):
    def run(self):
        comandos = {
            "1": AdicionarFornecedorEventoCommand(self.sistema),
            "2": ListarFornecedorEventoCommand(self.sistema),
            "3": AtualizarStatusFornecedorEventoCommand(self.sistema),
            "4": ImportarFornecedorCsvCommand(self.sistema),
        }

        opcoes = {
            "1": "Adicionar fornecedor",
            "2": "Listar fonecedores",
            "3": "Atualizar status do fornecedor",
            "4": "Importar fornecedores csv",
        }

        while True:
            print("\n --- Gerir Fornecedores ---")
            self.display_menu(opcoes)
            op = input("Opção: ")

            if op == "0":
                self.sistema.set_state(MenuPrincipalState(self.sistema))
                break
            comando = comandos.get(op)

            if comando:
                comando.executar()
            else:
                print("Opção Inválida")


class GestaoFinancasState(MaquinaEstados):
    def run(self):
        comandos = {
            "1": DefinirOrcamentoEventoCommand(self.sistema),
            "2": RegistrarDespesaEventoCommand(self.sistema),
            "3": VerfinancasEventoCommand(self.sistema),
            "4": RemoverDespesaEventoCommand(self.sistema),
        }

        opcoes = {
            "1": "Definir orçamento",
            "2": "Registrar despesa",
            "3": "Ver finanças",
            "4": "Remover despesa",
        }

        while True:
            print("\n --- Gerir Fornecedores ---")
            self.display_menu(opcoes)
            op = input("Opção: ")

            if op == "0":
                self.sistema.set_state(MenuPrincipalState(self.sistema))
                break
            comando = comandos.get(op)

            if comando:
                comando.executar()
            else:
                print("Opção Inválida")


class GestaoLocaisState(MaquinaEstados):
    def run(self):
        comandos = {
            "1": AdicionarLocalCommand(self.sistema),
            "2": ListarLocaisDisponiveisCommand(self.sistema),
            "3": RemoverLocalCommand(self.sistema),
            "4": ImportarLocaisCsvCommand(self.sistema),
        }

        opcoes = {
            "1": "Adicionar Local",
            "2": "Listar locais disponíveis",
            "3": "Remover Local",
            "4": "Importar csv",
        }

        while True:
            print("\n --- Gerir Fornecedores ---")
            self.display_menu(opcoes)
            op = input("Opção: ")

            if op == "0":
                self.sistema.set_state(MenuPrincipalState(self.sistema))
                break
            comando = comandos.get(op)

            if comando:
                comando.executar()
            else:
                print("Opção Inválida")
