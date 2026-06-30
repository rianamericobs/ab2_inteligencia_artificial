from criacionais.participanteModelo import Participante

class ParticipanteDecorator(Participante):
    def __init__(self, participanteEmbrulhado):
        self._participante = participanteEmbrulhado
    
    def to_dict(self):
        return self._participante.to_dict()
    def __getattr__(self, name): #Pega os atributos do participante
        return getattr(self._participante, name)

class BeneficioCamisaDecorator(ParticipanteDecorator):
    def to_dict(self):
        data = super().to_dict()
        data['beneficios'] = data.get('beneficios', []) + ['Camisa Oficial']
        return data

class BeneficioCelularDecorator(ParticipanteDecorator):
    def to_dict(self):
        data = super().to_dict()
        data['beneficios'] = data.get('beneficios', []) + ['Celular iphone']
        return data

class BeneficioCertificadoDecorator(ParticipanteDecorator):
    def to_dict(self):
        data = super().to_dict()
        data['beneficios'] = data.get('beneficios', []) + ['Certificado de participação']
        return data
    
