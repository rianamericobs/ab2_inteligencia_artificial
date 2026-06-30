# AB2 - Inteligencia Artificial (2026.1)

Disciplina: Inteligencia Artificial  
Professor: Evandro de Barros Costa

Este repositorio contem as atividades da Lista AB2, organizadas por questões.

## Questao 1 - Shell Generica de Sistema Baseado em Conhecimento

Objetivo:
- Implementar uma ferramenta generica para criar aplicacoes de diagnostico e recomendacao sem alterar o codigo-fonte, apenas definindo a base de conhecimento.

Arquitetura minima contemplada:
- Editor da Base de Conhecimento (cadastro, edicao, remocao e persistencia)
- Base de Conhecimento (fatos iniciais/inferidos, regras, hipoteses)
- Motor de Inferencia (Forward Chaining, Backward Chaining e estrategia hibrida)
- Mecanismo de Explicacao (respostas para "Por que?" e "Como?")
- Interface com usuario (CLI e Web)

Extensao com IA Generativa:
- Uso de LLM para interpretacao de linguagem natural, mapeamento de respostas, explicacoes mais naturais e apoio ao cadastro da base.
- O raciocinio principal permanece simbolico e baseado em regras.

Demonstracao:
- Base demonstrativa em dominio escolhido pela equipe (ex.: medico, automotivo, triagem etc.).

Entregaveis:
- Codigo-fonte da shell
- Base de conhecimento da demonstracao
- Relatorio tecnico
- Video/apresentacao

## Questao 2 - 2 Sistemas Escolhidos

### 2.1 Sistema de Perguntas e Respostas no estilo Akinator

Objetivo:
- Identificar uma entidade de um dominio especifico por meio de perguntas sequenciais com respostas Sim, Nao e Nao Sei.

Requisitos principais:
- Pelo menos 20 entidades
- Pelo menos 15 atributos
- Mecanismo de inferencia para reduzir hipoteses
- Interacao iterativa com exibicao da hipotese mais provavel

Experimentos esperados:
- Numero medio de perguntas
- Taxa de acerto
- Casos de falha
- Ambiguidade com multiplas hipoteses

Entregaveis:
- Codigo-fonte
- Base de conhecimento
- Relatorio tecnico
- Apresentacao/demonstracao

### 2.2 Sistema de Diagnostico Medico com Redes Bayesianas

Objetivo:
- Modelar e implementar uma Rede Bayesiana para inferencia diagnostica sob incerteza.

Requisitos principais:
- Pelo menos 1 doenca principal
- Minimo de 5 variaveis
- Pelo menos 3 sintomas observaveis
- Estrutura de dependencias e CPTs justificadas
- Inferencia em multiplos cenarios com atualizacao de probabilidades

Experimentos esperados:
- Inferencia inicial por sintomas
- Atualizacao com novas evidencias
- Comparacao entre conjuntos de evidencias

Entregaveis:
- Modelo da rede
- Arquivo do projeto da ferramenta
- Codigo-fonte (quando aplicavel)
- Relatorio tecnico
- Apresentacao/video

## Questao 3 - Aplicacao com Agentes Baseados em LLM

Objetivo:
- Construir uma aplicacao envolvendo agentes baseados em LLM.

Entregavel esperado:
- Aplicacao funcional demonstrando uso de agentes com LLM.
- Apresentacao/video

## Estrutura do Repositorio

- `questao1/` - Shell de sistema baseado em conhecimento
- `questao2/` - Sistemas da Questao 2 (2.1 e 2.2)
- `questao3/` - Aplicacao com agentes baseados em LLM
