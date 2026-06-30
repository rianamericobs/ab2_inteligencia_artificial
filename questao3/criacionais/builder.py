class EventoBuilder:
    def __init__(self, nome, data):
        self._evento_data = {
            'nome': nome,
            'data': data,
            'participantes': {},
            'fornecedores': {},
            'despesas': {},
            'speakers': {},
            'orcamento': 0.0,
            'local_reservado': None
        }

    def com_orcamento(self, valor):
        self._evento_data['orcamento'] = float(valor)
        return self # Retorna a própria instância para encadear chamadas

    def com_local(self, local_data):
        self._evento_data['local_reservado'] = local_data
        return self

    def build(self):
        """Retorna os dados do evento como um dicionário pronto para o Firebase."""
        return self._evento_data