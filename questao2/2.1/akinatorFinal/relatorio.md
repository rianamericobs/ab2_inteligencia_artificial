# Relatório Técnico - Mini Akinator

## 1. Descrição do domínio

O sistema foi desenvolvido para um domínio misto de personagens fictícios e jogadores brasileiros de futebol. A escolha foi feita para permitir a comparação entre entidades com características bem distintas, aumentando o poder discriminativo das perguntas e tornando a experiência semelhante a um jogo de adivinhação no estilo Akinator.

O domínio inclui personagens de jogos, animes, quadrinhos, filmes e atletas do futebol brasileiro. Apesar de heterogêneo, trata-se de um único universo de entidades conhecidas pelo usuário, o que permite criar perguntas objetivas sobre origem, tipo de mídia, poderes, profissão, posição em campo e outros traços marcantes.

## 2. Estratégia de representação do conhecimento

A base de conhecimento é armazenada em um arquivo JSON em `dados/personagens.json`. Essa base contém:

- uma lista de atributos/características que servem como perguntas do sistema;
- uma lista de entidades, cada uma com nome, descrição e valores booleanos para os atributos.

Cada atributo é uma característica do tipo sim/não, por exemplo:

- humano;
- protagonista;
- usa magia;
- tem superpoderes;
- pertence a jogos;
- é jogador de futebol;
- ganhou Copa do Mundo.

Essa representação é explícita, simples de manter e adequada ao objetivo educacional do projeto, pois facilita a consulta, a filtragem e a expansão da base.

## 3. Mecanismo de inferência utilizado

O sistema utiliza uma busca em espaço de hipóteses com filtragem progressiva dos candidatos. A abordagem pode ser descrita como um método híbrido com os seguintes componentes:

- **Baseado em regras**: cada resposta do usuário é comparada com os valores da base e entidades incompatíveis são removidas.
- **Busca em espaço de hipóteses**: o conjunto de candidatos é atualizado a cada resposta.
- **Seleção gulosa da próxima pergunta**: o sistema escolhe o atributo que melhor separa os candidatos restantes.
- **Ranking por similaridade**: quando não sobra certeza absoluta, a hipótese mais provável é escolhida pelo maior número de atributos compatíveis.

O sistema não usa uma árvore de decisão fixa nem uma rede bayesiana. Em vez disso, a árvore de perguntas é construída dinamicamente durante a interação, com base nas respostas do usuário e na distribuição dos candidatos.

## 4. Exemplos de interação

Exemplo simplificado:

```text
Pergunta: O personagem é humano?
Resposta: sim

Pergunta: É jogador ou jogadora de futebol?
Resposta: nao

Pergunta: Pertence a jogos eletrônicos?
Resposta: sim

Hipótese atual mais provável: Mario
```

Outro exemplo, com entidade do futebol:

```text
Pergunta: É jogador ou jogadora de futebol?
Resposta: sim

Pergunta: É brasileiro ou brasileira?
Resposta: sim

Pergunta: Ganhou a Bola de Ouro?
Resposta: sim

Hipótese atual mais provável: Kaká
```

O sistema também aceita respostas como `sim`, `nao` e `nao sei`, além de variações equivalentes.

## 5. Análise dos resultados obtidos

Foram realizados testes simulados com todas as entidades da base. O script de testes responde corretamente para cada alvo e mede o comportamento do mecanismo de inferência.

Resultados observados:

- taxa de acerto simulada: 100%;
- número médio de perguntas: 4,97;
- a maioria das entidades foi identificada com 4 a 6 perguntas.

Esses resultados indicam que a base está bem distribuída e que os atributos escolhidos têm bom poder de distinção. Como o sistema depende de respostas booleanas e de uma seleção gulosa de perguntas, o desempenho tende a ser bom quando a entidade possui traços bem diferenciados.

Casos de falha e limitações:

- quando o usuário responde de forma ambígua ou incoerente, o sistema pode cair para a melhor hipótese por similaridade;
- entidades muito parecidas podem permanecer candidatas por mais tempo;
- o domínio heterogêneo é funcional, mas exige boa documentação para justificar a seleção das entidades.

Mesmo com essas limitações, o sistema cumpre o objetivo proposto: representar conhecimento, perguntar de forma sequencial, eliminar hipóteses incompatíveis e concluir com a hipótese mais provável.

## 6. Conclusão

O Mini Akinator atende aos requisitos principais do enunciado. A solução usa uma base de conhecimento explícita, um mecanismo de raciocínio por filtragem de hipóteses e um critério de escolha de perguntas que melhora a separação entre candidatos. O resultado é um sistema explicável e adequado para fins acadêmicos.