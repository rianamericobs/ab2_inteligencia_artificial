from google import genai
from chave import senha
class LLMServico:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Iniciando conexão com a IA (Google Gemini)...")
            cls._instance = super(LLMServico, cls).__new__(cls)
            
            # Insira sua chave API real aqui
            chave_api = senha
            
            # Instancia o novo cliente
            cls._instance.client = genai.Client(api_key=chave_api)
            
        return cls._instance

llm_service_instance = LLMServico()