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

## Estratégia de inferência

O sistema a estratégia de busca em espaço de hipóteses:

- cada resposta do usuário atualiza o conjunto de candidatas;
- entidades incompatíveis são removidas;
- a próxima pergunta é escolhida pelo atributo que melhor separa os candidatos;
- quando não há certeza absoluta, o sistema usa um ranking por similaridade para escolher a hipótese mais provável.

Isso combina uma base de conhecimento explícita com um mecanismo de raciocínio heurístico, o que caracteriza um método híbrido entre regras de eliminação e seleção gulosa de perguntas.

## Relatório técnico

O arquivo com a descrição completa do domínio, da representação do conhecimento, do mecanismo de inferência, exemplos de interação e análise dos resultados está em `relatorio.md`.

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
