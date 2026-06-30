from .participanteModelo import Participante, ParticipanteRegular, ParticipanteVIP, ParticipanteEstudante
from estruturais.decorator import BeneficioCertificadoDecorator, BeneficioCamisaDecorator, BeneficioCelularDecorator
# --- A Fábrica ---
class ParticipanteFactory:
    @staticmethod
    def criar_participante(tipo, nome, email):
        participanteBase = None
        if tipo.lower() == 'vip':
            participanteBase = ParticipanteVIP(nome, email)
        elif tipo.lower() == 'regular':
            participanteBase =  ParticipanteRegular(nome, email)
        elif tipo.lower() == 'estudante':
            participanteBase = ParticipanteEstudante(nome, email)
        else:
            raise ValueError(f"Tipo de participante desconhecido: {tipo}")
        
        participanteDecorator = participanteBase

        #Todos os participantes tem direito ao certificado de participação
        if isinstance(participanteBase, (ParticipanteVIP, ParticipanteRegular, ParticipanteEstudante)):    
            participanteDecorator = BeneficioCertificadoDecorator(participanteDecorator)
        
        if isinstance(participanteBase,(ParticipanteVIP,ParticipanteEstudante)):
            participanteDecorator = BeneficioCamisaDecorator(participanteDecorator)

        if isinstance(participanteBase,(ParticipanteVIP)):
            participanteDecorator = BeneficioCelularDecorator(participanteDecorator)

        return participanteDecorator    
