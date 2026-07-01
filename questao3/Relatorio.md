## Relatório do Sistema e Uso da LLM

1. Visão Geral da Aplicação
A aplicação desenvolvida (iniciada por Eliane Lais de Melo Bastos e refatorada por Vítor Gabriel dos Santos Oliveira) consiste em um robusto Sistema de Gestão de Eventos construído em Python. O sistema permite a gestão integral de um evento, cobrindo funcionalidades como cadastro e cancelamento de eventos, controle de participantes (com categorias como VIP e Estudante), coordenação de fornecedores, controle financeiro (orçamentos e despesas), palestrantes e coleta de feedbacks.

A persistência de dados é feita na nuvem utilizando o Firebase Realtime Database. O grande diferencial técnico desta aplicação é sua arquitetura limpa, suportada por múltiplos Padrões de Projeto:

Padrões Criacionais: Uso de Singleton para garantir uma única conexão com o Firebase, Factory Method para centralizar a criação dos tipos de participantes e Builder para construir os dados de um evento em etapas.

Padrões Comportamentais: O fluxo de menus não utiliza if/else aninhados, mas sim o padrão State, garantindo que a aplicação transite fluidamente entre estados (Menu Principal, Gestão de Eventos, etc.). As ações do usuário são encapsuladas pelo padrão Command, e o padrão Observer garante que os participantes sejam notificados assim que um evento for cancelado.

Padrões Estruturais: A complexidade da inicialização do sistema é oculta pelo padrão Facade, objetos são enriquecidos dinamicamente pelo Decorator (como a atribuição de benefícios a participantes VIP) e dados externos via CSV são traduzidos pelo Adapter. O sistema também possui um tratamento forte de exceções personalizadas para validação de regras de negócio.

## Relatório de Integração da Inteligência Artificial (LLM)

- Propósito da Implementação:

No ecossistema atual do projeto, dados estruturados (valores financeiros, capacidades de locais, listas de fornecedores) são tratados de forma determinística pelos padrões implementados. No entanto, o sistema também possui dados não estruturados, principalmente os feedbacks textuais inseridos pelos participantes. A integração com um Modelo de Linguagem Grande (LLM) foi utilizada para transformar esses relatos em conhecimento gerencial e, na evolução da Questão 3, em ações automatizadas de melhoria.

- Evolução para Agente LLM:

A implementação não ficou limitada a uma chamada simples de IA para gerar um texto. Foi criado um agente mínimo baseado em LLM, capaz de executar ciclos curtos de observação, decisão e ação. Em cada execução, o agente seleciona um evento, lê os feedbacks cadastrados no Firebase, recebe um objetivo em linguagem natural informado pelo usuário e carrega registros históricos de sessões anteriores.

A partir desse contexto, a LLM decide a próxima ação em formato JSON estruturado. O sistema interpreta essa decisão e executa uma ferramenta interna correspondente. Dessa forma, a LLM não atua apenas como "respondedor", mas como componente decisório dentro de um fluxo controlado pela aplicação.

- Ferramentas Disponíveis para o Agente:

O agente possui um conjunto de ferramentas integradas ao próprio sistema:

* `RESUMIR`: compila os feedbacks e gera um resumo gerencial com sentimento geral, pontos fortes, problemas recorrentes e recomendações.
* `CRIAR_PLANO`: cria um plano de ação com área afetada, problema identificado, ação recomendada, responsável, prazo e prioridade.
* `REGISTRAR_PRIORIDADE`: registra a prioridade dos problemas mais importantes, junto com uma justificativa.
* `GERAR_ALERTA`: produz uma mensagem orientativa para a equipe organizadora.
* `ENCERRAR`: finaliza o ciclo quando as entregas principais já foram realizadas.

- Memória e Persistência:

Os resultados produzidos pelo agente são salvos no Firebase dentro do próprio evento, na estrutura `agente_llm`. O sistema registra resumos, planos de ação, prioridades, mensagens para equipe e sessões completas. Em novas execuções, o agente consulta essa memória histórica para considerar ações anteriores e evoluir o trabalho, em vez de tratar toda execução como se fosse a primeira.

Estruturas utilizadas:

* `agente_llm/resumos`
* `agente_llm/planos_acao`
* `agente_llm/prioridades`
* `agente_llm/mensagens_equipe`
* `agente_llm/sessoes`

- Valor Gerado:

Com essa abordagem, o sistema deixa de ser apenas um repositório de eventos e feedbacks e passa a funcionar como uma ferramenta de apoio à decisão. O gestor não precisa analisar manualmente todos os comentários dos participantes; o agente resume os dados, identifica gargalos, propõe planos, registra prioridades e orienta a equipe organizadora.

Além disso, a arquitetura preserva os padrões de projeto já existentes. O acionamento do agente foi integrado ao menu por meio do padrão Command, exposto pela Facade e executado sobre a lógica central do `sistemaEvento.py`, mantendo a organização da aplicação.

- Exemplo de Execução:

Um objetivo possível para o agente é:

`Analise os feedbacks dos participantes considerando também as sessões anteriores do agente. Gere um resumo atualizado, revise o plano de ação já criado, registre as prioridades mais importantes e oriente a equipe organizadora sobre os próximos passos para melhorar a próxima edição do evento.`

Com esse objetivo, o agente pode executar uma sequência como:

1. `RESUMIR`: consolidar os feedbacks.
2. `CRIAR_PLANO`: propor ações práticas.
3. `REGISTRAR_PRIORIDADE`: definir o que deve ser tratado primeiro.

Esse comportamento demonstra o uso de LLM como agente porque existe percepção do contexto, tomada de decisão estruturada, execução de ferramentas, persistência de memória e continuidade entre sessões.
