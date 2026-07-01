# Mini Akinator

Sistema inteligente de perguntas e respostas inspirado no Akinator.

## Domínio

A base de conhecimento contém personagens fictícios e jogadores brasileiros de futebol.

## Requisitos atendidos

- Base com 30 entidades.
- Base com 40 atributos/características.
- Perguntas sequenciais ao usuário.
- Respostas aceitas: `sim`, `nao` e `nao sei`.
- Exibição da hipótese atual mais provável.
- Eliminação de hipóteses incompatíveis com as respostas.
- Ranking por similaridade quando não há certeza absoluta.
- Explicação da conclusão ao final.
- Testes simulados para calcular média de perguntas e taxa de acerto.

## Arquivos

```text
mini_akinator.py
/testes_akinator.py
/dados/personagens.json
README.md
```

## Como executar o jogo

No terminal, entre na pasta do projeto e execute:

```bash
python mini_akinator.py
```

Durante a execução, responda às perguntas usando uma das opções:

```text
sim
nao
nao sei
```

Também são aceitas variações como `s`, `n`, `não`, `?` e `talvez`.

## Como executar os testes simulados

```bash
python testes_akinator.py
```

Os testes simulam um usuário respondendo corretamente para cada entidade da base. Ao final, o programa mostra:

- Quantidade de perguntas usadas para cada entidade.
- Resposta escolhida pelo sistema.
- Se o sistema acertou ou falhou.
- Número médio de perguntas.
- Taxa de acerto simulada.

## Base de conhecimento

A base fica em:

```text
dados/personagens.json
```

Ela está em JSON e possui:

- `dominio`: descrição geral do domínio.
- `descricao`: finalidade da base.
- `atributos`: perguntas usadas pelo sistema.
- `entidades`: personagens e jogadores que podem ser adivinhados.

Cada entidade possui:

- `nome`.
- `descricao`.
- `atributos` com valores `true` ou `false`.

## Padrão de nomenclatura

Os identificadores do código Python foram ajustados para camelCase, por exemplo:

- `carregarBase`
- `normalizarResposta`
- `candidatosCompativeis`
- `escolherMelhorPergunta`
- `mostrarHipotese`
- `atributosPerguntados`
- `entidadeEscolhida`

Os atributos da base JSON também usam camelCase quando possuem mais de uma palavra, por exemplo:

- `usaMagia`
- `temSuperpoderes`
- `origemJaponesa`
- `jogadorFutebol`
- `ganhouCopaMundo`
- `jogouSelecaoBrasileira`
