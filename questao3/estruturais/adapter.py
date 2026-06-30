import csv
from criacionais.builder import EventoBuilder
from criacionais.factory import ParticipanteFactory 

class LocaisCsvAdapter():
    def __init__(self, caminhoArquivo):
        self._caminhoArquivo = caminhoArquivo
    
    def obterLocais(self):
        locais ={}

        try:
            with open(self._caminhoArquivo, mode = 'r', encoding='utf-8') as arquivo:
                leitor_csv = csv.DictReader(arquivo)
                for linha in leitor_csv:
                    #"Tradução"
                    nome_local = linha['nome_do_espaco']
                    locais[nome_local]= {
                        'nome': nome_local,
                        'endereco': linha['morada_completa'],
                        'capacidade': int(linha['lotacao_maxima'])
                    }
            
            return locais
        except FileNotFoundError:
            print(f"Erro do adaptador: Arquivo não encontrado em {self._caminhoArquivo}")
            return None
        except Exception as e:
            print(f"Erro do Adaptador ao processar o arquivo: {e}")
            return None

class ParticipanteCsvAdapter:
    def __init__(self, caminhoArquivo):
        self._caminhoArquivo = caminhoArquivo
    
    def obter_participantes(self):
        participantes_adaptados = {}

        try:
            with open(self._caminhoArquivo, mode='r', encoding='utf-8') as arquivo:
                leitor_csv = csv.DictReader(arquivo)
                
                print("\nA ler arquivo CSV de participantes...")
                for linha in leitor_csv:
                    try:

                        nome = linha['nome']
                        email = linha['email']
                        tipo = linha['tipo']

                        participante = ParticipanteFactory.criar_participante(tipo, nome, email)
                        
                        # Adiciona o participante ao dicionário, usando o seu ingresso único como chave.
                        #    O método .to_dict() converte o objeto para o formato do Firebase.
                        participantes_adaptados[participante.ingresso] = participante.to_dict()

                    except KeyError as e:
                        print(f"Erro de Adaptador: A coluna {e} não foi encontrada no arquivo CSV. A verificar a próxima linha.")
                        continue
                    except ValueError as e:
                        print(f"Erro de Adaptador: {e}. A verificar a próxima linha.")
                        continue

            print(f"{len(participantes_adaptados)} participantes processados com sucesso.")
            return participantes_adaptados

        except FileNotFoundError:
            print(f"Erro do Adaptador: arquivo não encontrado em '{self._caminhoArquivo}'")
            return None
        except Exception as e:
            print(f"Erro do Adaptador ao processar o arquivo: {e}")
            return None

class FornecedorCsvAdapter:
    def __init__(self, caminho_arquivo):
        self._caminho_arquivo = caminho_arquivo
    
    def obterFornecedores(self):
        
        fornecedores = []

        try:
            with open(self._caminho_arquivo, mode='r', encoding='utf-8') as arquivo:
                leitor_csv = csv.DictReader(arquivo)
                
                print("\nA ler ficheiro CSV de fornecedores...")
                for linha in leitor_csv:
                    try:
                        fornecedor_data = {
                            'nome': linha['fornecedor'],
                            'servico': linha['servico'], 
                            'contato': linha['contato'],
                            'status': 'Pendente'  
                        }
                        
                        fornecedores.append(fornecedor_data)

                    except KeyError as e:
                        print(f"Erro de Adaptador: A coluna {e} não foi encontrada no arquivo CSV. A verificar a próxima linha.")
                        continue

            return fornecedores

        except FileNotFoundError:
            print(f"Erro do Adaptador: arquivo não encontrado em '{self._caminho_arquivo}'")
            return None
        except Exception as e:
            print(f"Erro do Adaptador ao processar o arquivo: {e}")
            return None
        
