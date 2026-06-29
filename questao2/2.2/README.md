# Sistema de Diagnóstico Médico - Redes Bayesianas 🩺📊

Este diretório contém a solução para a **Questão 2.2** da avaliação de Inteligência Artificial (AB2). 

O projeto consiste no desenvolvimento de um sistema inteligente de diagnóstico médico utilizando **Redes Bayesianas** para inferir a probabilidade de um paciente estar infectado com **Dengue** ou **Chikungunya**, com base em sintomas observados (evidências).

## 📂 Estrutura do Diretório

* `redes_bayesianas.py`: Código-fonte principal em Python. Contém a modelagem da rede (nós e arestas), as Tabelas de Probabilidades Condicionais (CPTs) e o motor de inferência matemática.
* `relatorio.md`: Relatório técnico detalhando a escolha do domínio, a justificativa das probabilidades, a modelagem conceitual da rede e a análise crítica dos resultados obtidos.

## 🚀 Tecnologias e Bibliotecas

* **Linguagem:** Python 3
* **Biblioteca Principal:** `pgmpy` (Probabilistic Graphical Models using Python)

## ⚙️ Como Instalar e Executar

1. Certifique-se de que tem o Python instalado na sua máquina.
2. Instale a biblioteca `pgmpy` executando o seguinte comando no terminal:
   ```bash
   pip install pgmpy
   ```
3. Execute o script principal para visualizar os testes de inferência no terminal:
   ```bash
   python redes_bayesianas.py
   ```

## 🧠 Experimentos Realizados

O script executa automaticamente três cenários de inferência diagnóstica para demonstrar o funcionamento do Teorema de Bayes e a atualização das probabilidades *a posteriori*:

* **Experimento 1:** Inferência diagnóstica a partir de sintomas iniciais observados (Febre Alta e Dor Articular).
* **Experimento 2:** Atualização dinâmica do diagnóstico após a inclusão de um novo sintoma ao quadro clínico (Manchas na Pele).
* **Experimento 3:** Comparação da inferência com um conjunto de evidências diferente (presença de febre e manchas, mas negação de dor articular).

---
