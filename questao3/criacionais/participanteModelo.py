import random

# --- Classe Base ---
class Participante:
    def __init__(self, nome, email):
        if "@" not in email:
            raise ValueError("Erro: O email deve conter o caractere '@'.")
        self.nome = nome
        self.email = email
        self.tipo = "Indefinido"
        self.ingresso = self._gerar_ingresso()

    def _gerar_ingresso(self):
        return f"ING{random.randint(1000, 9999)}"

    def to_dict(self):
        """Converte o objeto para um dicionário para ser guardado no Firebase."""
        return {'nome': self.nome, 'email': self.email, 'tipo': self.tipo}

# --- Classes Concretas ---
class ParticipanteRegular(Participante):
    def __init__(self, nome, email):
        super().__init__(nome, email)
        self.tipo = "Regular"

class ParticipanteVIP(Participante):
    def __init__(self, nome, email):
        super().__init__(nome, email)
        self.tipo = "VIP"
        # VIPs podem ter benefícios extras no futuro
        self.acesso_lounge = True

    def to_dict(self):
        # Sobrescreve o método para adicionar dados extras
        data = super().to_dict()
        data['acesso_lounge'] = self.acesso_lounge
        return data

class ParticipanteEstudante(Participante):
    def __init__(self, nome, email):
        super().__init__(nome,email)
        self.tipo = "Estudante"
