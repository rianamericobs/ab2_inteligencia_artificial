
class NotificacaoObservador:
    def __init__(self,notificacoes_ref):
        self.notificacoes_ref = notificacoes_ref
    
    def atualizar( self, nomeEvento, listaEmail):
        print("Padrão Observer detectado. Criando notificaçõse no firebase.")
        mensagem = f"O evento {nomeEvento} foi cancelado."

        for email in listaEmail:
            notificacaoData = {
                'emailDestinatario': email,
                'mensagem': mensagem,
                'lida': False
            }
            self.notificacoes_ref.push(notificacaoData)