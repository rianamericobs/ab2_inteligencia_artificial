## Créditos e Autoria

Este projeto foi desenvolvido em duas fases distintas, com contribuições fundamentais de diferentes autores:

### Projeto Original

* **Autora:** Eliane Lais de Melo Bastos
* **Git:** LaisMelo22
* **Contribuição:** Concepção e implementação inicial das funcionalidades principais do sistema de gestão de eventos, como parte da disciplina de Projeto de Software.

### Refatoração e Arquitetura de Software

* **Autor:** Vítor Gabriel dos Santos Oliveira
* **Git:** VtrGbr
* **Contribuição:** Responsável pela refatoração do projeto, migração para o Firebase Realtime Database e pela implementação de uma arquitetura avançada baseada nos seguintes padrões de projeto:
    * **Criacionais:** Singleton, Factory Method, Builder.
    * **Comportamentais:** State, Command, Observer.
    * **Estruturais:** Facade, Decorator, Adapter.

# Sistema de Gestão de Eventos

Uma implementação em Python de um sistema de gestão de eventos, utilizando Firebase como base de dados e aplicando padrões de projeto de software para uma arquitetura robusta e escalável. 
Este projeto foi originalmente desenvolvido pela aluna ELIANE LAIS DE MELO BASTOS da matéria Projeto de Software e após a troca dos projetos fiquei com este projeto e fiquei com a responsabilidade de implementar os padrões de projeto.

## Funcionalidades Implementadas

* **Gestão de Eventos:** Criação, cancelamento e listagem de eventos.
* **Gestão de Participantes:** Adição de diferentes tipos de participantes (Regular, VIP, Estudante) com benefícios automáticos, listagem e remoção.
* **Gestão de Locais:**  Adição, listagem e remoção de locais, com a capacidade de importar locais a partir de ficheiros CSV.
* **Notificações:** Sistema de notificação (via Firebase) para o cancelamento de eventos.
* **Gestão Financeira:** Definição de orçamento e registo de despesas por evento.
* **Coordenação de Fornecedores:** Gestão completa de fornecedores, incluindo adição, listagem e atualização de status.
* **Gestão de Palestrantes (Speakers):** Adição, listagem e remoção de palestrantes de um evento.
* **Feedback e Pesquisas:** Criação de pesquisas e recolha de feedback dos participantes.
* **Análise por IA:** A inteligência artificial resume os feedbacks do evento e identifica sentimento geral, pontos fortes, problemas recorrentes e recomendações.
* **Agente LLM de Melhoria:** Além de responder uma análise pontual, o sistema possui um agente baseado em LLM que executa ciclos curtos de observação, decisão e ação. O agente recebe um objetivo em linguagem natural, consulta os feedbacks e a memória histórica salva no Firebase, decide a próxima ação em JSON estruturado e executa ferramentas internas para resumir feedbacks, criar plano de ação, registrar prioridades e gerar mensagens para a equipe.

---

## Agente LLM de Melhoria de Eventos

A Questão 3 foi implementada como uma aplicação com agente baseado em LLM dentro do sistema de gestão de eventos. O agente não apenas gera texto: ele analisa o estado do evento, decide uma ação, executa uma ferramenta do sistema e registra o resultado no Firebase.

Fluxo geral do agente:

1. O usuário escolhe um evento com feedbacks cadastrados.
2. O usuário informa um objetivo, por exemplo: "analisar feedbacks, gerar relatório, planejar melhorias e orientar a equipe".
3. O agente compila os feedbacks e carrega a memória histórica de execuções anteriores.
4. A LLM decide a próxima ação em JSON estruturado.
5. O sistema executa a ferramenta correspondente.
6. Os resultados são salvos no Firebase e a sessão é registrada.

Ferramentas disponíveis para o agente:

* `RESUMIR`: gera um resumo gerencial dos feedbacks.
* `CRIAR_PLANO`: cria um plano de ação com área, problema, ação, responsável, prazo e prioridade.
* `REGISTRAR_PRIORIDADE`: registra prioridade e justificativa para os principais problemas.
* `GERAR_ALERTA`: gera uma mensagem orientativa para a equipe organizadora.
* `ENCERRAR`: finaliza o ciclo quando as entregas principais já foram feitas.

Dados gravados no Firebase:

* `eventos/<nome_evento>/agente_llm/resumos`
* `eventos/<nome_evento>/agente_llm/planos_acao`
* `eventos/<nome_evento>/agente_llm/prioridades`
* `eventos/<nome_evento>/agente_llm/mensagens_equipe`
* `eventos/<nome_evento>/agente_llm/sessoes`

Para executar pelo menu:

```bash
python evento.py
```

Depois selecione:

```text
1. Gerir Evento
12. Executar agente de melhoria com IA
```

---

## Configuração e Instalação

Para executar este projeto, são necessários alguns passos de configuração, principalmente para a ligação com a base de dados Firebase.

### Pré-requisitos

* Python 3.x
* Conta Google para aceder ao Firebase

### 1. Clonar o Repositório

```bash
git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git) cd seu-repositorio 
```

#  Instalar dependências
    Este projeto requer a biblioteca firebase-admin. Instale-a usando o pip:

2. Instale as dependências:
Certifique-se de instalar os pacotes necessários para o Firebase e para a nova inteligência artificial:

```bash
pip install firebase-admin google-genai
```
3. Configure as Chaves de API:
Firebase: Adicione o seu arquivo JSON de credenciais do Firebase na pasta adequada (conforme estruturado no firebaseServico).

Google Gemini: No arquivo criacionais/llmServico.py, insira sua chave de API gerada no Google AI Studio na variável correspondente.

```bash
pip install firebase-admin
```

# Configurar a Base de Dados Firebase

O sistema utiliza o Firebase Realtime Database para armazenar todos os dados. Siga estes passos:

1. Acesse o Console do Firebase e crie um novo projeto.

2. No menu do projeto, vá para Build > Realtime Database e crie uma nova base de dados. Pode começar no modo de teste para permitir leituras e escritas.

3. Vá para Configurações do Projeto (ícone de engrenagem) > Contas de serviço.

4. Clique em "Gerar nova chave privada". Será feito o download de um ficheiro .json.

5. **IMPORTANTE**: Renomeie este ficheiro para projetorefatorado-firebase-adminsdk-fbsvc-d9be3a5d92.json e coloque-o na pasta raiz do seu projeto. O ficheiro .gitignore já está configurado para impedir que este ficheiro sensível seja enviado para o GitHub.

# Como Executar
Após concluir a configuração, execute o ficheiro principal para iniciar o menu interativo:
```bash
python evento.py
```
# Arquitetura e Padrões de Projeto
O projeto foi desenhado com uma arquitetura limpa, separando as responsabilidades em diferentes camadas e aplicando um conjunto completo de padrões de projeto para garantir um código flexível e de alta qualidade.

Estrutura de Ficheiros
O projeto está organizado da seguinte forma:

- criacionais/: Contém os padrões responsáveis pela criação de objetos (Singleton, Factory, Builder).

- comportamentais/: Contém os padrões que gerem a comunicação e o fluxo da aplicação (Command, Observer, State).

- estruturais/: Contém os padrões que lidam com a composição e a relação entre objetos (Decorator, Facade, Adapter).

- sistemaEvento.py: O coração do sistema, contendo a lógica de negócio principal.

- evento.py: O ponto de entrada da aplicação, responsável por iniciar a Facade.

### Padrões de projeto utilizados

## Padrões de Projeto Criacionais Utilizados
- Singleton (firebaseServico.py): Garante uma única instância da ligação com o Firebase, otimizando recursos e a gestão do estado da ligação.

- Factory Method (factory.py): Utilizado para criar diferentes tipos de Participante. Centraliza a lógica de instanciação, permitindo a fácil adição de novos tipos sem alterar o código cliente.

- Builder (builder.py): Empregado para construir o objeto de Evento de forma passo a passo, simplificando a criação de um objeto complexo com múltiplos atributos.

## Padrões de Projeto Comportamentais Utilizados
- State (state.py): Gere o fluxo da aplicação como uma máquina de estados finitos. Cada menu (Menu Principal, Gerir Eventos, etc.) é um estado, o que organiza a navegação e elimina a necessidade de menus aninhados.

- Command (command.py): Encapsula cada ação do utilizador (como "criar evento" ou "listar participantes") num objeto. Isto elimina longos blocos if/elif nos menus e desacopla quem invoca a ação de quem a executa.

- Observer (observer.py): Usado para desacoplar o cancelamento de um evento da notificação aos participantes. Quando um evento é cancelado, ele notifica os "observadores" (como o serviço de notificação) sem precisar de conhecer os detalhes da sua implementação.

## Padrões de Projeto Estruturais Utilizados
- Facade (facade.py): Fornece um ponto de entrada único e simplificado para o sistema. O ficheiro evento.py interage apenas com a Facade, que esconde toda a complexidade de inicialização e configuração do sistema.

- Decorator (decorator.py): Adiciona benefícios (como "Camisa" ou "Certificado") a objetos Participante dinamicamente. Está integrado com a Factory para que os participantes já sejam criados com os seus benefícios padrão.

- Adapter (adapter.py): Atua como um "tradutor" para permitir que o sistema importe dados de fontes externas com formatos incompatíveis, como ficheiros CSV de locais, sem alterar a lógica de negócio existente.
