from criacionais.factory import ParticipanteFactory #Factory method
from criacionais.firebaseServico import firebase_service_instance # singleton
from criacionais.builder import EventoBuilder #Builder

from comportamentais.command import *
from comportamentais.observer import NotificacaoObservador
from comportamentais.state import MenuPrincipalState

from estruturais.decorator import *
from estruturais.adapter import LocaisCsvAdapter, ParticipanteCsvAdapter, FornecedorCsvAdapter

from tratar.excessoes import *
from datetime import datetime
from criacionais.llmServicos import llm_service_instance


class SistemaEventos:
    def __init__(self):
        self._observadores = [] # observer
        #Agora usaremos a instância única do Singleton para aceder às referências
        self.db_service = firebase_service_instance
        self.eventos_ref = self.db_service.eventos_ref
        self.locais_ref = self.db_service.locais_ref
        self.notificacoes_ref = self.db_service.notificacoes_ref

        #state
        self._state = MenuPrincipalState(self)

    # ==== State
    def set_state(self, novoEstado):
        
        self._state = novoEstado
        print(f"---- Mudança de Estado {novoEstado} ----")
    
    def ExecutarEstado(self):
        while self._state is not None:
            self._state.run()

    #=== Observer
    def anexar(self,observador):
        self._observadores.append(observador)

    def notificar(self,nomeEvento,listaEmail):
        for observador in self._observadores:
            observador.atualizar(nomeEvento,listaEmail)
    
    

    def selecionar_evento(self):
        eventos = self.eventos_ref.get()
        if not eventos:
            print("Nenhum evento registado no Firebase.")
            return None

        eventos_lista = list(eventos.items())

        print("\nEventos disponíveis:")
        for i, (nome_evento, dados_evento) in enumerate(eventos_lista):
           
            data_evento = dados_evento.get('data', 'Sem data')
            print(f"{i}. {nome_evento} (Data: {data_evento})")

        try:
            idx_str = input("Selecione o evento pelo número: ")
         
            if not idx_str.isdigit():
                print("Seleção inválida. Por favor, digite um número.")
                return None
            
            idx = int(idx_str)
            if 0 <= idx < len(eventos_lista):
                return eventos_lista[idx][0]
            else:
                print("Seleção inválida.")
                return None
                
        except ValueError: 
            print("Seleção inválida.")
            return None

    def analisar_feedbacks_com_llm(self):
        sel = self.selecionar_evento()
        if not sel: return

        # Pega todos os feedbacks do evento no Firebase
        feedbacks = self.eventos_ref.child(sel).child('feedbacks').get()

        if not feedbacks:
            print("Nenhum feedback registrado para este evento para ser analisado.")
            return

        print("\nProcessando feedbacks com Inteligência Artificial...")
        
        # Compila os textos para enviar à LLM
        textos_feedback = []
        for fb_id, fb_data in feedbacks.items():
            for pergunta, resposta in fb_data['respostas'].items():
                textos_feedback.append(f"Pergunta: {pergunta} | Resposta: {resposta}")

        compilado = "\n".join(textos_feedback)
        
        prompt = f"""
        Você é um assistente de gestão de eventos. Aqui estão os feedbacks do evento '{sel}':
        {compilado}
        
        Por favor, faça um resumo gerencial destes feedbacks informando:
        1. Sentimento geral dos participantes (positivo, neutro ou negativo).
        2. Principais pontos fortes mencionados.
        3. Principais pontos de melhoria ou reclamações.
        """

        try:
            # No novo SDK, usamos o 'client.models.generate_content' e passamos o nome do modelo (vamos usar o mais recente: gemini-2.5-flash)
            resposta_ia = llm_service_instance.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            print(f"\n--- Análise da IA sobre os Feedbacks do Evento: {sel} ---")
            print(resposta_ia.text)
            print("-" * 50)
        except Exception as e:
            print(f"Erro ao comunicar com a LLM: {e}")
   

    def criar_evento(self):
        print("\n--- Criação de Novo Evento ---")
   
        nome = input("Nome do evento: ")
        if not nome:
            raise NomeInvalidoError("O nome não pode estar vazio")
        if nome.isdigit():
            raise NomeInvalidoError("O nome do evento não pode ser um número!")
        
        eventoExistente = self.eventos_ref.child(nome).get()
        if eventoExistente:
            raise EventoJaExistenteError(f"Já existe um evento com o nome: {nome}")
        
        data = input("Data (dd/mm/aaaa): ")
        if not data:
            raise DataInvalidaError("A data do evento não pode estar vazia")
        
        try:
            dataEvento = datetime.strptime(data, '%d/%m/%Y').date()
            if dataEvento < datetime.now().date():
                raise DataInvalidaError("A data do evento não pode ser uma data no passado.")
        except ValueError:
            raise DataInvalidaError("O formato da data deve ser dd/mm/aaaa e a data deve ser válida.")
        
        orcamento_str = input("Definir orçamento inicial (opcional): ")

        try:
            builder = EventoBuilder(nome, data)
            
            if orcamento_str:
                try:
                    builder.com_orcamento(orcamento_str)
                except ValueError:
                    
                    raise OrcamentoInvalidoError(f"Valor de orçamento '{orcamento_str}' inválido. Use apenas números.")

            novo_evento_data = builder.build()
            self.eventos_ref.child(nome).set(novo_evento_data)
            
            
            print(f"SUCESSO: Evento '{nome}' criado com sucesso!")

        except OrcamentoInvalidoError as e:
            
            raise e
        except Exception as e:
            # Apanha erros de gravação no Firebase
            raise Exception(f"Erro ao salvar o evento no Firebase: {e}")

    def cancelar_evento(self):
        nome_evento = self.selecionar_evento()
        if not nome_evento:
            return

        # 1. Obter os dados do evento diretamente do Firebase
        evento_ref = self.eventos_ref.child(nome_evento)
        dados_evento = evento_ref.get()

        if not dados_evento:
            print("Evento não encontrado no Firebase.")
            return

        # 2. Obter a lista de e-mails dos participantes a partir dos dados do Firebase
        lista_emails = []
        if 'participantes' in dados_evento and dados_evento['participantes']:
            lista_emails = [p['email'] for p in dados_evento['participantes'].values()]

        # 3. Enviar os e-mails
        if lista_emails:
            self.notificar(nome_evento,lista_emails)
            
            print("Notificações criadas com sucesso.")
        else:
            print("Nenhum participante para notificar.")

        # 4. Remover o evento do Firebase
        try:
            evento_ref.delete()
            print(f"Evento '{nome_evento}' cancelado e removido do Firebase.")
        except Exception as e:
            print(f"Erro ao remover evento do Firebase: {e}")
    
    def listar_eventos(self):
        # Pega todos os dados do nó 'eventos'
        eventos = self.eventos_ref.get()
        if not eventos:
            print("Nenhum evento cadastrado.")
            return

        print("\nEventos cadastrados:")
        for nome_evento, dados_evento in eventos.items():
            print(f"- {dados_evento['nome']} ({dados_evento['data']})")

    def criar_survey_evento(self):
        sel = self.selecionar_evento()
        if not sel: return

        perguntas = []
        titulo = input("Título da pesquisa: ")
        print("Digite perguntas (deixe em branco e pressione Enter para encerrar):")
        while True:
            p = input("> ")
            if not p: break
            perguntas.append(p)

        # Prepara os dados da pesquisa para salvar no Firebase
        nova_survey_data = {
            'titulo': titulo,
            'perguntas': perguntas
        }

        # Salva a nova pesquisa no Firebase sob o evento selecionado
        try:
            # .push() cria um ID único para a pesquisa
            self.eventos_ref.child(sel).child('Enquete').push(nova_survey_data)
            print(f"Pesquisa '{titulo}' criada com sucesso no Firebase para o evento '{sel}'.")
        except Exception as e:
            print(f"Erro ao salvar a pesquisa no Firebase: {e}")

    def coletar_feedback_evento(self):
        sel = self.selecionar_evento()
        if not sel: return

        # Primeiro, verifica se o ingresso do participante existe no evento
        ingresso = input("Confirme seu Ingresso: ")
        participantes_ref = self.eventos_ref.child(sel).child('participantes')
        participantes = participantes_ref.get()

        if not participantes or ingresso not in participantes:
            print("Ingresso não encontrado para este evento.")
            return

        # Busca a pesquisa mais recente do evento no Firebase
        surveys_ref = self.eventos_ref.child(sel).child('Enquete')
        todas_surveys = surveys_ref.order_by_key().limit_to_last(1).get()

        if not todas_surveys:
            print("Nenhuma pesquisa disponível para este evento.")
            return

        # Pega o ID e os dados da última pesquisa adicionada
        id_survey, dados_survey = list(todas_surveys.items())[0]

        respostas = {}
        print(f"\n--- Respondendo à Pesquisa: {dados_survey['titulo']} ---")
        for pergunta in dados_survey['perguntas']:
            respostas[pergunta] = input(f"{pergunta}: ")

        # Prepara os dados do feedback para salvar
        novo_feedback_data = {
            'ingresso_participante': ingresso,
            'respostas': respostas,
            'id_pesquisa': id_survey # Guarda a referência de qual pesquisa foi respondida
        }

        # Salva o feedback no Firebase
        try:
            self.eventos_ref.child(sel).child('feedbacks').push(novo_feedback_data)
            print("Feedback registrado com sucesso. Obrigado por participar!")
        except Exception as e:
            print(f"Erro ao salvar o feedback no Firebase: {e}")

    def listar_feedbacks_evento(self):
        sel = self.selecionar_evento()
        if not sel: return

        # Pega todos os feedbacks do evento no Firebase
        feedbacks = self.eventos_ref.child(sel).child('feedbacks').get()

        if not feedbacks:
            print("Nenhum feedback registrado para este evento.")
            return

        print(f"\n--- Feedbacks do Evento: {sel} ---")
        # Itera sobre cada feedback (cada um com seu ID único)
        for fb_id, fb_data in feedbacks.items():
            print(f"\nFeedback (Participante com Ingresso: {fb_data['ingresso_participante']})")
            for pergunta, resposta in fb_data['respostas'].items():
                print(f"- {pergunta}: {resposta}")
            print("-" * 20)


    def adicionar_speaker_evento(self):
        sel = self.selecionar_evento()
        if not sel: return
        try:    
            # Coleta as informações do palestrante
            nome = input("Nome do palestrante: ")
            if not nome:
                raise NomeInvalidoError("O campo nome não pode estar vazio!")
            if nome.isdigit():
                raise NomeInvalidoError("O nome não pode ser um número!")
            bio = input("Bio: ")

            if not bio or bio.isdigit():
                raise NomeInvalidoError("O campo não pode ser um número ou estar vazio!")
            email = input("Email: ")

            if "@" not in email:
                raise EmailInvalidoError("O email deve conter o @!")
            topico = input("Tópico da palestra: ")

            if not topico or topico.isdigit():
                raise TopicoInvalidoError("Tópico não pode ser um número ou estar vazio!")
            horario = input("Horário (ex: 14:30): ")

            # Estrutura os dados para salvar no Firebase
            novo_speaker_data = {
                'nome': nome,
                'bio': bio,
                'email': email,
                'topico': topico,
                'horario': horario
            }

        # Salva o novo palestrante no Firebase
        
            self.eventos_ref.child(sel).child('Palestrante').push(novo_speaker_data)
            print(f"Palestrante '{nome}' adicionado com sucesso ao evento '{sel}'.")
        except Exception as e:
            print(f"Erro ao salvar o palestrante no Firebase: {e}")

    def listar_speakers_evento(self):
        sel = self.selecionar_evento()
        if not sel: return

        # Pega todos os palestrantes do evento no Firebase
        speakers = self.eventos_ref.child(sel).child('Palestrante').get()

        if not speakers:
            print("Nenhum palestrante cadastrado para este evento.")
            return

        print(f"\n--- Palestrantes do Evento: {sel} ---")
        # Itera sobre cada palestrante (cada um com seu ID único)
        for speaker_id, speaker_data in speakers.items():
            print(f"\nNome: {speaker_data['nome']}")
            print(f"  Tópico: '{speaker_data['topico']}' às {speaker_data['horario']}")
            print(f"  Email: {speaker_data['email']}")
            print(f"  ID para remoção: {speaker_id}") # Mostra o ID
        print("-" * 20)
        return speakers # Retorna os dados para serem usados pela função de remoção

    def remover_speaker_evento(self):
        sel = self.selecionar_evento()
        if not sel: return

        # Primeiro, lista os palestrantes para o usuário ver os IDs
        speakers = self.listar_speakers_evento()
        if not speakers:
            return # Se não houver palestrantes, encerra a função

        # Pede ao usuário o ID do palestrante a ser removido
        speaker_id_para_remover = input("\nDigite o ID do palestrante que deseja remover: ")

        # Verifica se o ID fornecido existe antes de tentar remover
        if speaker_id_para_remover in speakers:
            try:
                # Remove o palestrante do Firebase usando seu ID único
                speaker_nome = speakers[speaker_id_para_remover]['nome']
                self.eventos_ref.child(sel).child('Palestrante').child(speaker_id_para_remover).delete()
                print(f"Palestrante '{speaker_nome}' removido com sucesso.")
            except Exception as e:
                print(f"Erro ao remover o palestrante do Firebase: {e}")
        else:
            print("ID inválido ou não encontrado.")
   

   # ==== Participantes
    #factory method
    def adicionar_participante_evento(self):
        sel = self.selecionar_evento()
        if not sel: return
        try :
            nome = input("Nome: ") 
            
            if not nome:
                raise NomeInvalidoError("O campo de nome não pode estar vazio")
            
            if nome.isdigit():
                raise NomeInvalidoError("O nome do palestrante não pode conter números!")
            
            
            email = input("Email: ")
            if '@' not in email:
                raise EmailInvalidoError("O email deve conter o caracter @ ")
            
            tipo = input("Tipo de participante (Regular/Vip/Estudante): ")

            if not tipo:
                raise NomeInvalidoError("O campo 'tipo' não pode estar vazio")
            
            if tipo.isdigit():
                raise NomeInvalidoError(" O tipo do participante não pode ser um número")
        except Exception as e:
            print(f"Erro inesperado: {e}")    
        try:
            # Usa a Factory para criar o objeto do tipo correto
            participante = ParticipanteFactory.criar_participante(tipo, nome, email)
            
            # Converte o objeto para dicionário e guarda no Firebase
            self.eventos_ref.child(sel).child('participantes').child(participante.ingresso).set(participante.to_dict())
            print(f"Participante '{nome}' ({participante.tipo}) adicionado com sucesso!")
            print(f"Ingresso: {participante.ingresso}")
        except ValueError as e:
            print(f"Erro: {e}")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")

    def listar_participantes_evento(self):
        sel = self.selecionar_evento()
        if not sel: return

        # Obtém os dados dos participantes do Firebase
        participantes = self.eventos_ref.child(sel).child('participantes').get()

        if not participantes:
            print("Nenhum participante registado para este evento.")
            return

        print(f"\n--- Participantes do Evento: {sel} ---")
        for ingresso, dados in participantes.items():
            print(f"- {dados['nome']} ({dados['email']}) | Ingresso: {ingresso}")

    def excluir_participante_evento(self):
        sel = self.selecionar_evento()
        if not sel: return

        ingresso_para_remover = input("Digite o Ingresso do participante a ser removido: ")

        # Ponto de referência para o participante específico
        participante_ref = self.eventos_ref.child(sel).child('participantes').child(ingresso_para_remover)

        # Verifica se o participante existe antes de tentar remover
        if not participante_ref.get():
            print("Ingresso não encontrado.")
            return

        try:
            # Remove o participante do Firebase
            participante_ref.delete()
            print(f"Participante com ingresso '{ingresso_para_remover}' removido com sucesso.")
        except Exception as e:
            print(f"Erro ao remover participante: {e}")


    # ==== Fornecedor
    def adicionar_fornecedor_evento(self):
        sel = self.selecionar_evento()
        if not sel: return
        try:    
            nome = input("Nome do fornecedor: ")

            if not nome:
                raise NomeInvalidoError("O campo nome não pode estar vazio")
            if nome.isdigit():
                raise NomeInvalidoError("O nome do fonecedor não pode ser um número")
            
            servico = input("Serviço prestado: ")
            if not servico:
                raise ServicoInvalidoError("Informe o serviço prestado!")
            
            contato = input("Telefone[(xx)-xxxx-xxxx] ou email (opcional): ")

            if contato:
                is_email = "@" in contato
                is_celular = contato.replace('-', '').replace('(', '').replace(')', '').replace(' ', '').isdigit()
                if not is_email and not is_celular:
                    raise ContatoInvalidoError("O contato deve ser um e-mail válido (com '@') ou um número de telefone (apenas dígitos).")

            fornecedor_data = {
                'nome': nome,
                'servico': servico,
                'contato': contato,
                'status': 'Pendente'
            }

            # Adiciona o fornecedor com um ID único
            self.eventos_ref.child(sel).child('fornecedores').push(fornecedor_data)
            print(f"Fornecedor '{nome}' adicionado com sucesso.")
        except Exception as e:
            print(f"Erro ao adicionar fornecedor: {e}")

    def listar_fornecedores_evento(self):
        sel = self.selecionar_evento()
        if not sel: return

        fornecedores = self.eventos_ref.child(sel).child('fornecedores').get()

        if not fornecedores:
            print("Nenhum fornecedor registado para este evento.")
            return None # Retorna None se não houver fornecedores

        print(f"\n--- Fornecedores do Evento: {sel} ---")
        for fid, dados in fornecedores.items():
            print(f"Nome: {dados['nome']} | Serviço: {dados['servico']} | Status: {dados['status']}")
            print(f"  ID para atualização: {fid}")
        return fornecedores

    def atualizar_status_fornecedor_evento(self):
        sel = self.selecionar_evento()
        if not sel: return

        # Lista os fornecedores para o utilizador ver os IDs
        fornecedores = self.listar_fornecedores_evento()
        if not fornecedores:
            return

        fid_para_atualizar = input("\nDigite o ID do fornecedor para atualizar o status: ")
        if fid_para_atualizar not in fornecedores:
            print("ID inválido.")
            return

        novo_status = input("Digite o novo status (ex: Confirmado, Pago): ")

        try:
            # Atualiza apenas o campo 'status' do fornecedor
            fornecedor_ref = self.eventos_ref.child(sel).child('fornecedores').child(fid_para_atualizar)
            fornecedor_ref.update({'status': novo_status})
            print("Status do fornecedor atualizado com sucesso!")
        except Exception as e:
            print(f"Erro ao atualizar status: {e}")


    # === Financeiro
    def definir_orcamento_evento(self):
        sel = self.selecionar_evento()
        if not sel: return

        try:
            valor = float(input("Digite o valor do orçamento: R$ "))
            if not valor:
                raise ValorInvalidoError("O campo valor não pode estar vazio!")
            
            if valor < 0:
                raise ValorInvalidoError("Digite um valor válido")
            # Guarda o orçamento diretamente no nó do evento
            self.eventos_ref.child(sel).update({'orcamento': valor})
            print(f"Orçamento de R${valor:.2f} definido para o evento '{sel}'.")
        except ValueError:
            print("Erro: Por favor, digite um número válido.")
        except Exception as e:
            print(f"Erro ao definir o orçamento: {e}")


    def registrar_despesa_evento(self):
        sel = self.selecionar_evento()
        if not sel: return

        # Obter os dados financeiros atuais
        dados_evento = self.eventos_ref.child(sel).get()

        orcamento = dados_evento.get('orcamento', 0.0)

        despesas = dados_evento.get('despesas', {})

        total_gasto = sum(item['valor'] for item in despesas.values())

        saldo = orcamento - total_gasto

        print(f"\nSaldo atual: R${saldo:.2f}")

        try:
            descricao = input("Descrição da despesa: ")

            if not descricao:
                raise NomeInvalidoError("O campo descrição não pode estar vazio!")
            
            if descricao.isdigit():
                raise NomeInvalidoError("A descrição não pode ser um número")
        except Exception as e:
            print(f"Erro inesperado: {e}")
            
        try:
            valor = float(input("Valor da despesa: R$ "))
            if valor < 0 or not valor:
                raise ValueError()
        except ValueError:
            print("Erro: Por favor, digite um número válido.")
            return
        
        if valor > saldo:
            print(f"Erro: A despesa de R${valor:.2f} excede o saldo disponível de R${saldo:.2f}.")
            return
        try:    
            categoria = input("Categoria da despesa (ex: Catering, Marketing, Local): ")

            if not categoria:
                raise CategoriaInvalidaError("A categoria não pode ser vazia!")
            
            if categoria.isdigit():
                raise CategoriaInvalidaError("Categoria não pode ser um número")
            try:
                data = input("Data da despesa (dd/mm/aaaa): ")
                dataEvento = datetime.strptime(data, '%d/%m/%Y').date()

                if dataEvento < datetime.now().date():
                    raise DataInvalidaError(" A data não pode ser uma ja ocorrida")
            except ValueError:
                raise DataInvalidaError("O formato da data deve ser dd/mm/aaaa e a data deve ser válida")
            
            despesaDados = {
                'descricao': descricao,
                'valor': valor,
                'data': data,
                'categoria': categoria
            }

        
            self.eventos_ref.child(sel).child('despesas').push(despesaDados)
            print("Despesa registada com sucesso.")
        except Exception as e:
            print(f"Erro ao registar a despesa: {e}")

    def ver_financas_evento(self):
        sel = self.selecionar_evento()
        if not sel: return

        dados_evento = self.eventos_ref.child(sel).get()
        if not dados_evento:
            print("Evento não encontrado.")
            return

        orcamento = dados_evento.get('orcamento', 0.0)
        despesas = dados_evento.get('despesas', {})

        total_gasto = sum(item['valor'] for item in despesas.values())
        saldo = orcamento - total_gasto

        # Agrupar despesas por categoria
        despesas_por_categoria = {}
        for item in despesas.values():
            categoria = item.get('categoria', 'Sem Categoria')
            if categoria not in despesas_por_categoria:
                despesas_por_categoria[categoria] = []
            despesas_por_categoria[categoria].append(item)

        print(f"\n--- Relatório Financeiro do Evento: {sel} ---")
        print(f"Orçamento Total: R${orcamento:.2f}")
        
        print("\n--- Despesas por Categoria ---")
        if not despesas_por_categoria:
            print("Nenhuma despesa registada.")
        else:
            for categoria, items in despesas_por_categoria.items():
                total_categoria = sum(d['valor'] for d in items)
                print(f"\nCategoria: {categoria} (Total: R${total_categoria:.2f})")
                for item in items:
                    print(f"  - {item['descricao']} (R${item['valor']:.2f}) em {item['data']}")

        print("\n" + "="*30)
        print(f"Total Gasto: R${total_gasto:.2f}")
        print(f"Saldo Disponível: R${saldo:.2f}")
        if saldo < 0:
            print("ATENÇÃO: O orçamento foi excedido!")
        print("="*30)


    def remover_despesa_evento(self):
        sel = self.selecionar_evento()
        if not sel: return

        despesas_ref = self.eventos_ref.child(sel).child('despesas')
        despesas = despesas_ref.get()

        if not despesas:
            print("Nenhuma despesa registada para remover.")
            return

        print("\n--- Despesas Registadas ---")
        for despesa_id, dados in despesas.items():
            print(f"-> Descrição: {dados['descricao']} | Valor: R${dados['valor']:.2f}")
            print(f"   ID para remoção: {despesa_id}")

        id_para_remover = input("\nDigite o ID da despesa que deseja remover: ")

        if id_para_remover not in despesas:
            print("ID inválido.")
            return

        try:
            despesas_ref.child(id_para_remover).delete()
            print("Despesa removida com sucesso!")
        except Exception as e:
            print(f"Erro ao remover a despesa: {e}")

    # === Local

    def adicionar_local(self):
        print("\n---Adicionar um novo local---")
        try:
            nome = input("Nome do local: ")

            if not nome:
                raise NomeInvalidoError("O campo nome não pode estar vazio")
            if nome.isdigit():
                raise NomeInvalidoError("A localidade não pode ser um número")
            localExistente = self.locais_ref.child(nome).get()

            if localExistente:
                raise LocalJaExistenteError("Este local já foi adicionado")
            endereco = input("Endereço: ")

            if not endereco:
                raise EnderecoInvalidoError("O campo de endereço não pode estar vazio!")
        
        
            capacidade = int(input("Capacidade: "))
            
            if not capacidade.is_integer() or capacidade < 0:
                raise CapacidadeInvalidaError("Capacidade deve ser um número válido")
            #Guardar no fire base
            local_data={
                'nome': nome,
                'endereco': endereco,
                'capacidade': capacidade
            }
        except Exception as e:
            print(f"Erro inesperado: {e}")

        try:
            self.locais_ref.child(nome).set(local_data)
            print(f"Local '{nome}' adicionado com sucesso! ")
        except Exception as e:
            print("Erro ao guardar o local no Firebase: {e}")
    
    def listar_locais_disponiveis(self):
        print("\n--- Locais Disponíveis ---")
        locais = self.locais_ref.get()

        if not locais:
            print("Nenhum local registrado")
            return
        for nome, dados in locais.items():
            print(f"- {dados['nome']} ({dados['endereco']} - Capacidade {dados['capacidade']})")
        return locais
    
    
    def reservar_local_evento(self):
        sel = self.selecionar_evento()
        if not sel: return
        
        #Carregando os locais disponiveis
        print("-- Carregando os locais disponiveis")
        locaisDisponiveis = self.locais_ref.get()

        if not locaisDisponiveis:
            print("Nenhum local disponível para reserva. Adicione um local primeiro no menu 'Gerir locais")
            return
        
        #Transformar o dicionario em uma lista
        locais_lista = list(locaisDisponiveis.values())

        print("\n--- Escolha um local para fazer a reserva ---")
        for i, local in enumerate(locais_lista):
            print(f"{i}. {local['nome']} ({local['endereco']}) - Capacidade: {local['capacidade']}")

        try:
            index = int(input("Selecione o local pelo número: "))

            if index < 0:
                raise IndexError
            local_escolhido = locais_lista[index]

            #preparar os dados do local para guardar no evento
            local_data ={
                'nome': local_escolhido['nome'],
                'endereco': local_escolhido['endereco'],
                'capacidade': local_escolhido['capacidade']
            }    

            self.eventos_ref.child(sel).child('local_reservado').set(local_data)
            print(f"Local '{local_escolhido['nome']}' reservado com sucesso para o evento '{sel}'.")
        except (ValueError, IndexError):
            print("Seleção inválida.")
        except Exception as e:
            print(f"Ocorreu um erro ao reservar o local: {e}")
    
    def remover_local(self):

        locaisExistentes = self.listar_locais_disponiveis()
        if not locaisExistentes:
            return
        localidade = input("Digite o local que deseja remover: ")
        
        
        if localidade not in locaisExistentes:
            print("Esta localidade não se encontra no banco de dados.")
            return
        localRemover_ref = self.locais_ref.child(localidade)
           

        try:
            # Remove o participante do Firebase
            localRemover_ref.delete()
            print(f"O local '{localidade}' removido com sucesso.")
        except Exception as e:
            print(f"Erro ao remover localiade: {e}")
    

    # === Adapter
    def importar_locais_de_csv(self):
        print("\n--- Importar Locais do csv ---")
        caminho = input("Digite o caminho para o arquivo csv: ")
        
        # O sistema não sabe como ler um CSV. Ele apenas sabe que o adaptador
        # tem um método .obter_locais() que lhe devolverá os dados no formato correto.
        adaptador = LocaisCsvAdapter(caminho)
        novos_locais = adaptador.obterLocais() #Retorna um dicionario para colocar no banco de dados
        
        if novos_locais:
            # O método .update() do Firebase adiciona ou atualiza os locais
            self.locais_ref.update(novos_locais)
            print(f"\n{len(novos_locais)} locais foram importados com sucesso!")

    def importar_participantes_csv(self):
        print("\n--- Importar Participantes de um arquivo csv ---")

        sel = self.selecionar_evento()
        if not sel:
            return

        caminho = input("Digite o caminho para o arquivo csv: ")

        adaptador = ParticipanteCsvAdapter(caminho)
        novos_participantes = adaptador.obter_participantes()

        if novos_participantes:
            try:
                
                participantes_ref = self.eventos_ref.child(sel).child('participantes')
                
                
                participantes_ref.update(novos_participantes)
                
                print(f"\n{len(novos_participantes)} participantes foram importados com sucesso para o evento '{sel}'!")
            except Exception as e:
                print(f"Ocorreu um erro ao guardar os participantes no Firebase: {e}")
    
    def importar_fornecedor_csv(self):
        print("\n--- Importar Fornecedores de um arquivo csv ---")
        
        sel = self.selecionar_evento()
        if not sel:
            return
        
        caminho = input("Digite o nome do arquivo csv: ")

        adaptador = FornecedorCsvAdapter(caminho)

        fornecedores = adaptador.obterFornecedores()

        if fornecedores:
            try:
                fornecedores_ref = self.eventos_ref.child(sel).child('fornecedores')
                
                for fornecedor_data in fornecedores:
                    fornecedores_ref.push(fornecedor_data)

                print(f"\n{len(fornecedores)} fornecedores foram importados com sucesso para o evento '{sel}'!")
            except Exception as e:
                print(f"Ocorreu um erro ao guardar os fornecedores no Firebase: {e}")
