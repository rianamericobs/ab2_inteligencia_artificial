from sistemaEvento import SistemaEventos, NotificacaoObservador
from estruturais.facade import SistemaFacade

if __name__ == "__main__":
    facade = SistemaFacade()
    facade.iniciarAplicacao()
    print("\nSistema pronto. A instância do Firebase foi carregada.")