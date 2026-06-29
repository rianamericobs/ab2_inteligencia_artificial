# RELATÓRIO TÉCNICO: Sistema Inteligente de Diagnóstico Médico Utilizando Redes Bayesianas

**Disciplina:** Inteligência Artificial

**Docente:** Evandro de Barros Costa

## 1. Descrição do Domínio

O domínio médico escolhido para este sistema de diagnóstico é o das doenças infecciosas tropicais, especificamente o diagnóstico diferencial entre **Dengue** e **Chikungunya**. A escolha deste domínio justifica-se pela alta prevalência dessas arboviroses no Brasil e pela dificuldade no diagnóstico clínico inicial, uma vez que ambas compartilham sintomas muito semelhantes (como febre alta e manchas na pele). No entanto, a intensidade e a presença de certos sintomas, como dores articulares severas, apresentam probabilidades diferentes dependendo da doença, o que torna as Redes Bayesianas uma ferramenta ideal para lidar com a incerteza desse diagnóstico.

## 2. Modelagem da Rede

A rede bayesiana foi modelada para representar a relação de causa e efeito entre as doenças (nós pais) e os sintomas observáveis (nós filhos). O modelo foi implementado na linguagem Python, utilizando a biblioteca `pgmpy` (classe `DiscreteBayesianNetwork`).

A rede é composta por 5 variáveis booleanas (Sim / Não):

* **Hipóteses (Doenças):** `Dengue`, `Chikungunya`.
* **Evidências (Sintomas observáveis):** `Febre_Alta`, `Dor_Articular`, `Manchas_Pele`.

**Relações de dependência:**
A presença de uma ou ambas as doenças causa os sintomas. Logo, as arestas da rede partem de `Dengue` e `Chikungunya` e apontam diretamente para `Febre_Alta`, `Dor_Articular` e `Manchas_Pele`. Assumiu-se a independência condicional dos sintomas entre si, dado o estado das doenças.

## 3. Tabelas de Probabilidades Condicionais (CPTs)

As probabilidades foram definidas de forma plausível para fins educacionais, refletindo o conhecimento médico geral de que a Chikungunya causa dores articulares mais intensas, enquanto a Dengue é mais comumente associada à febre inicial.

**Probabilidades a priori (Prevalência base):**

* P(Dengue = Sim) = 15%
* P(Chikungunya = Sim) = 5%

**CPT 1: Febre Alta**

| Dengue | Chikungunya | P(Febre = Sim) | P(Febre = Não) |
| --- | --- | --- | --- |
| Sim | Sim | 99% | 1% |
| Sim | Não | 90% | 10% |
| Não | Sim | 95% | 5% |
| Não | Não | 5% | 95% |

**CPT 2: Dor Articular (Intensa)**

| Dengue | Chikungunya | P(Dor = Sim) | P(Dor = Não) |
| --- | --- | --- | --- |
| Sim | Sim | 95% | 5% |
| Sim | Não | 40% | 60% |
| Não | Sim | 90% | 10% |
| Não | Não | 10% | 90% |

**CPT 3: Manchas na Pele**

| Dengue | Chikungunya | P(Manchas = Sim) | P(Manchas = Não) |
| --- | --- | --- | --- |
| Sim | Sim | 80% | 20% |
| Sim | Não | 50% | 50% |
| Não | Sim | 60% | 40% |
| Não | Não | 5% | 95% |

## 4. Exemplos de Inferência (Experimentos)

Foram realizados três cenários de testes utilizando o motor de inferência por Eliminação de Variáveis (`VariableElimination`) da biblioteca `pgmpy`.

* **Experimento 1: Inferência diagnóstica a partir de sintomas observados.**
* *Evidências:* Febre = Sim, Dor Articular = Sim.
* *Resultado Interpretado:* A presença de febre aumenta a probabilidade de ambas as doenças. Contudo, a inclusão da "Dor Articular" atua como um forte indício, elevando significativamente a probabilidade a posteriori de Chikungunya, que originalmente era de apenas 5%.


* **Experimento 2: Atualização do diagnóstico após a inclusão de novos sintomas.**
* *Evidências:* Febre = Sim, Dor Articular = Sim, Manchas = Sim.
* *Resultado Interpretado:* O paciente retorna relatando um novo sintoma. O sistema recalcula as probabilidades a posteriori de forma dinâmica. O surgimento de manchas consolida a crença de que o paciente possui uma arbovirose, mantendo altas as chances de Dengue e Chikungunya em relação a outras causas genéricas.


* **Experimento 3: Comparação entre diferentes conjuntos de evidências.**
* *Evidências:* Febre = Sim, Dor Articular = Não, Manchas = Sim.
* *Resultado Interpretado:* Neste cenário, o paciente possui febre e manchas, mas *não* tem dor articular. Como a ausência de dor articular severa é muito rara na Chikungunya (P(Dor=Não|C=Sim) = 10%), a rede penaliza drasticamente a probabilidade de Chikungunya, tornando a Dengue a hipótese esmagadoramente mais provável.



## 5. Análise e Discussão dos Resultados

**Como a rede representa a incerteza:**
Diferente da lógica clássica, o sistema não afirma com 100% de certeza que um paciente tem Dengue. Ele utiliza o Teorema de Bayes para combinar a crença inicial (prevalência das doenças) com a força das evidências (sintomas), atualizando o grau de crença (probabilidade) de 0 a 1 à medida que novas informações são disponibilizadas.

**A influência de cada evidência no diagnóstico:**
Ficou claro nos experimentos que a evidência "Dor Articular = Sim" tem um peso forte para a Chikungunya, enquanto "Dor Articular = Não" atua como um fator de exclusão prática para essa doença, favorecendo a Dengue. A "Febre" funciona como um sintoma gatilho amplo, que aumenta a suspeita de ambas as doenças em relação ao estado normal.

**Vantagens das Redes Bayesianas em relação a sistemas baseados apenas em regras:**
Sistemas de regras tradicionais (Ex: `SE febre E manchas ENTÃO Dengue`) são frágeis diante de incertezas e informações incompletas. Se o paciente não souber informar sobre as manchas, uma regra rígida pode falhar. A Rede Bayesiana, por outro lado, continua fornecendo um diagnóstico probabilístico mesmo que apenas um sintoma seja conhecido, lidando naturalmente com dados ausentes ou ruidosos.

**Limitações da modelagem desenvolvida:**
A principal limitação é o pressuposto de independência condicional rígida adotada (modelo do tipo *Naive Bayes* para os sintomas). Na vida real, a ocorrência simultânea de manchas e dores pode ter correlações adicionais que não dependem apenas da doença. Além disso, as probabilidades inseridas (CPTs) foram estimadas para fins didáticos e não substituem dados epidemiológicos reais.
