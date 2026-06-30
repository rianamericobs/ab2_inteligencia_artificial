import firebase_admin
from firebase_admin import credentials, db
import sys 
import os

def resource_path(relative_path):
   
    try:
       
        base_path = sys._MEIPASS
    except Exception:  
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class FirebaseServico:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("A criar a instância do FirebaseService...")
            cls._instance = super(FirebaseServico, cls).__new__(cls)
            try:
                json_key_path = resource_path("projetorefatorado-firebase-adminsdk-fbsvc-d9be3a5d92.json")
                #Credencial
                cred = credentials.Certificate(json_key_path)
                # URL do banco de dados
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://projetorefatorado-default-rtdb.firebaseio.com/'
                })
                print("Conexão Firebase iniciada com sucesso.")
            except ValueError as e:
                print(f"Firebase já iniciado: {e}")
            
            # Referências do banco de dados
            cls._instance.eventos_ref = db.reference('eventos')
            cls._instance.locais_ref = db.reference('locais')
            cls._instance.notificacoes_ref = db.reference('notificacoes')
            
        return cls._instance

# Exporta a instância única
firebase_service_instance = FirebaseServico()