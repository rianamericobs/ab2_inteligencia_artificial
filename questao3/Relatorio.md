## Relatório do Sistema e Uso da LLM

1. Visão Geral da Aplicação
A aplicação desenvolvida (iniciada por Eliane Lais de Melo Bastos e refatorada por Vítor Gabriel dos Santos Oliveira) consiste em um robusto Sistema de Gestão de Eventos construído em Python. O sistema permite a gestão integral de um evento, cobrindo funcionalidades como cadastro e cancelamento de eventos, controle de participantes (com categorias como VIP e Estudante), coordenação de fornecedores, controle financeiro (orçamentos e despesas), palestrantes e coleta de feedbacks.

A persistência de dados é feita na nuvem utilizando o Firebase Realtime Database. O grande diferencial técnico desta aplicação é sua arquitetura limpa, suportada por múltiplos Padrões de Projeto:

Padrões Criacionais: Uso de Singleton para garantir uma única conexão com o Firebase, Factory Method para centralizar a criação dos tipos de participantes e Builder para construir os dados de um evento em etapas.

Padrões Comportamentais: O fluxo de menus não utiliza if/else aninhados, mas sim o padrão State, garantindo que a aplicação transite fluidamente entre estados (Menu Principal, Gestão de Eventos, etc.). As ações do usuário são encapsuladas pelo padrão Command, e o padrão Observer garante que os participantes sejam notificados assim que um evento for cancelado.

Padrões Estruturais: A complexidade da inicialização do sistema é oculta pelo padrão Facade, objetos são enriquecidos dinamicamente pelo Decorator (como a atribuição de benefícios a participantes VIP) e dados externos via CSV são traduzidos pelo Adapter. O sistema também possui um tratamento forte de exceções personalizadas para validação de regras de negócio.

## Relatório de Integração da Inteligência Artificial (LLM)

- Propósito da Implementação:

No ecossistema atual do projeto, dados estruturados (valores financeiros, capacidades de locais, listas de fornecedores) são tratados de forma determinística pelos padrões implementados. No entanto, o sistema possuía dados não estruturados sob a forma de feedbacks inseridos pelos participantes. A implementação de um Modelo de Linguagem Grande (LLM) serviu para extrair inteligência de negócio desse texto livre.

- Como funciona e o Valor Gerado:

Através de um novo serviço (Singleton) conectado à API do Google Gemini, a aplicação agora consegue buscar no Firebase todas as pesquisas de satisfação de um evento e injetá-las em um prompt estruturado. A IA avalia o texto, compreende o contexto e devolve um resumo tático, informando o sentimento predominante da plateia, bem como agrupando pontos fortes e gargalos do evento.

Isso eleva a aplicação de um simples banco de registros para uma ferramenta analítica de gestão. O gestor do evento não precisa mais ler dezenas de feedbacks individuais para entender o que deu errado; a IA resume tudo através do padrão de acionamento em comando implementado, respeitando a arquitetura refatorada do software.