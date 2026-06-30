# AB2 - Inteligência Artificial (2026.1)

Disciplina: Inteligência Artificial  
Professor: Evandro de Barros Costa

Este repositório contém as atividades da Lista AB2, organizadas por questões.

## Questão 1 - Shell Genérica de Sistema Baseado em Conhecimento

Objetivo:
- Implementar uma ferramenta genérica para criar aplicações de diagnóstico e recomendação sem alterar o código-fonte, apenas definindo a base de conhecimento.

Arquitetura mínima contemplada:
- Editor da Base de Conhecimento (cadastro, edição, remoção e persistência)
- Base de Conhecimento (fatos iniciais/inferidos, regras, hipóteses)
- Motor de Inferência (Forward Chaining, Backward Chaining e estratégia híbrida)
- Mecanismo de Explicação (respostas para "Por quê?" e "Como?")
- Interface com usuário (CLI e Web)

Extensão com IA Generativa:
- Uso de LLM para interpretação de linguagem natural, mapeamento de respostas, explicações mais naturais e apoio ao cadastro da base.
- O raciocínio principal permanece simbólico e baseado em regras.

Demonstração:
- Base demonstrativa em domínio escolhido pela equipe (ex.: médico, automotivo, triagem etc.).

Entregáveis:
- Código-fonte da shell
- Base de conhecimento da demonstração
- Relatório técnico
- Vídeo/apresentação

## Questão 2 - 2 Sistemas Escolhidos

### 2.1 Sistema de Perguntas e Respostas no estilo Akinator

Objetivo:
- Identificar uma entidade de um domínio específico por meio de perguntas sequenciais com respostas Sim, Não e Não Sei.

Requisitos principais:
- Pelo menos 20 entidades
- Pelo menos 15 atributos
- Mecanismo de inferência para reduzir hipóteses
- Interação iterativa com exibição da hipótese mais provável

Experimentos esperados:
- Número médio de perguntas
- Taxa de acerto
- Casos de falha
- Ambiguidade com multiplas hipoteses

Entregáveis:
- Código-fonte
- Base de conhecimento
- Relatório técnico
- Apresentação/demonstração

### 2.2 Sistema de Diagnóstico Médico com Redes Bayesianas

Objetivo:
- Modelar e implementar uma Rede Bayesiana para inferência diagnóstica sob incerteza.

Requisitos principais:
- Pelo menos 1 doença principal
- Mínimo de 5 variáveis
- Pelo menos 3 sintomas observáveis
- Estrutura de dependências e CPTs justificadas
- Inferência em múltiplos cenários com atualização de probabilidades

Experimentos esperados:
- Inferência inicial por sintomas
- Atualização com novas evidências
- Comparação entre conjuntos de evidências

Entregáveis:
- Modelo da rede
- Arquivo do projeto da ferramenta
- Código-fonte (quando aplicável)
- Relatório técnico
- Apresentação/vídeo

## Questão 3 - Aplicação com Agentes Baseados em LLM

Objetivo:
- Construir uma aplicação envolvendo agentes baseados em LLM.

Entregável esperado:
- Aplicação funcional demonstrando uso de agentes com LLM.
- Apresentação/vídeo

## Estrutura do Repositório

- `questao1/` - Shell de sistema baseado em conhecimento
- `questao2/` - Sistemas da Questão 2 (2.1 e 2.2)
- `questao3/` - Aplicação com agentes baseados em LLM
