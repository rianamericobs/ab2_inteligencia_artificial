# K-RuleShell — Relatório Técnico
**Sistema Genérico para Construção de Aplicações Baseadas em Conhecimento**
**Foco: Diagnóstico e Classificação de Domínios**

---

## 1. Arquitetura Geral do Sistema

O sistema foi evoluído de uma aplicação baseada apenas em terminal para uma solução híbrida moderna, organizada em sete módulos principais:

```
questao1/
├── core/
│   ├── knowledge_base.py     # Base de Conhecimento, Fatos, Regras e Validações
│   ├── inference_engine.py   # Motor de Inferência (Forward / Backward / Híbrido)
│   ├── explanation.py        # Mecanismo de Explicação (Por quê / Como)
│   ├── kb_editor.py          # Editor interativo e persistência
│   └── llm_client.py         # Cliente LLM (Integração Groq)
├── ui/
│   └── cli.py                # Interface de Linha de Comando (Terminal)
├── web/
│   ├── server.py             # Backend FastAPI & Gerenciador de Sessões Multi-threaded
│   └── static/               # Frontend (HTML, CSS e JavaScript)
└── main.py                   # Ponto de entrada do Console CLI
```

### 1.1 Diagrama Conceitual da Interface Web

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Cliente Browser (Frontend)                      │
│     [HTML/CSS UI] ◄──► [app.js State] ──(Fetch API)──► [FastAPI App]   │
└─────────────────────────────────────────────────────────────┬──────────┘
                                                              │
┌─────────────────────────────────────────────────────────────▼──────────┐
│                        FastAPI Server (Backend)                        │
│                                                                        │
│  ┌──────────────────┐      (Thread Control)      ┌──────────────────┐  │
│  │   API Endpoints  │ ◄────────────────────────► │  SessionState    │  │
│  │   (HTTP routes)  │                            │  (Background Th) │  │
│  └──────────────────┘                            └────────┬─────────┘  │
│                                                           │            │
│                                                  ┌────────▼─────────┐  │
│                                                  │  Engine & Trace  │  │
│                                                  └──────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Estrutura de Representação do Conhecimento

### 2.1 Base de Conhecimento Domain-Agnostic
Para manter o núcleo do sistema 100% genérico, todos os limites de domínio e regras de negócio foram removidos do código-fonte Python e estruturados dinamicamente em metadados dentro da base de conhecimento:
* `attribute_ranges`: Mapa serializável contendo limites de valores livres (`[min_val, max_val]`) para atributos numéricos.
* `questions`: Mapa de perguntas personalizadas associadas a atributos.
* `answer_options`: Mapa de opções de resposta pré-definidas (ex: `["sim", "nao"]`).

### 2.2 Fatos, Condições e Regras
* **Fact**: Representa uma variável do domínio contendo nome do atributo, valor atribuído, origem (`"user"`, `"initial"`, ou `"inferred"`) e o Fator de Certeza (`cf`) de `0.0` a `1.0`.
* **Condition**: Suporta comparações lógicas usando os operadores `=`, `!=`, `>`, `<`, `>=`, `<=`.
* **Rule**: Regras de produção do tipo *SE-ENTÃO* contendo identificador único (`id`), prioridade (`priority`), lista de condições, operador de conjunção/disjunção das condições (`condition_operator` como `"AND"` ou `"OR"`) e o Fator de Certeza próprio da regra (`cf`).
* **Conclusion**: Representa o fato concluído e seu Fator de Certeza próprio (`cf`).

---

## 3. Estratégia de Inferência e Fallback de Metas

### 3.1 Algoritmo Híbrido (Hybrid Chaining)
O motor executa uma consulta inteligente em três fases:
1. **Fase Forward**: Propaga quaisquer fatos já presentes na memória de trabalho para deduzir conclusões imediatas.
2. **Fase Backward**: Para cada hipótese configurada, tenta prová-la recursivamente gerando sub-metas. Caso um fato falte e não haja regra para prová-lo, o motor aciona o callback de pergunta ao usuário.
3. **Fase Forward Final**: Processa os novos fatos informados pelo usuário para atualizar conclusões secundárias.

### 3.2 Inferência de Hipóteses (Fallback)
Se uma base de conhecimento for carregada sem nenhuma hipótese configurada no campo `"hypotheses"`, o motor analisa as regras cadastradas em tempo de execução e **estabelece todas as conclusões das regras como hipóteses alvo**. Isso permite que bases de conhecimento criadas de maneira livre funcionem instantaneamente no modo de consulta sem a necessidade de pré-configurações rígidas de hipóteses.

---

## 4. Integração com Inteligência Artificial

A inteligência artificial atua através de chamadas estruturadas de API em três componentes:
1. **Mapeamento de Linguagem Natural (`map_answer_to_options`)**: Converte respostas descritivas livres do usuário em opções exatas da base de dados (ex: *"Com certeza"* -> *"sim"*).
2. **Explicação Narrativa (`explain_natural_language`)**: Converte a árvore de regras disparada pelo mecanismo formal em uma explicação fluida e compreensível em português.
3. **Assistente de Cadastro Lote (`ia`)**: Interpreta comandos em português livre e gera estruturas JSON completas para regras e perguntas (incluindo intervalos de limites de forma autônoma).

### 4.1 Implementação do Mecanismo de Explicação (Por quê / Como)
O mecanismo de explicação é implementado pela classe `ExplanationEngine` (`core/explanation.py`) e consome a trilha de inferência registrada em `InferenceTrace` (`core/inference_engine.py`).

Durante a execução, o motor registra:
* **Passos de inferência (`steps`)**: regra aplicada, estratégia usada (forward/backward), condições satisfeitas, conclusão e CF calculado.
* **Perguntas feitas ao usuário (`questions_asked`)**: atributo perguntado e justificativa textual do motivo da pergunta.
* **Pilha de objetivos (`goal_stack`)**: sequência de metas ativas no backward chaining para contextualizar o raciocínio.

Com esses dados, o sistema oferece quatro visões explicativas:
1. **why(atributo)**: informa por que um atributo foi perguntado, incluindo regras dependentes e meta corrente.
2. **how(atributo, valor)**: reconstrói passo a passo a cadeia de regras que produziu uma conclusão específica.
3. **full_trace()**: exibe a trilha completa da sessão de inferência.
4. **session_summary()**: resume fatos iniciais, fatos do usuário e fatos inferidos com seus respectivos CFs.

Essa arquitetura separa claramente inferência (cálculo) e explicação (interpretação), permitindo auditoria e depuração sem acoplar lógica de apresentação ao motor.

---

## 5. Gerenciamento de Sessões Web (FastAPI)

Para que a interface web consuma o motor de inferência (que executa de forma síncrona/bloqueante no console), implementamos um **SessionManager** multi-threaded no backend FastAPI:
* Cada sessão ativa gera um identificador único (`session_id`) e clona a Base de Conhecimento para evitar interferência entre usuários concorrentes.
* O motor de inferência é executado em uma **Thread secundária de segundo plano**.
* Quando o motor necessita de informações, o callback de pergunta escreve a pergunta na sessão e entra em estado de espera usando um evento de sincronização (`threading.Event.wait()`).
* A API recebe a resposta do frontend, executa as validações de limites em tempo real (`validate_free_input`), grava o valor validado e libera a thread especialista (`threading.Event.set()`).

---

## 6. Verificação e Testes

* **Interface Visual**: Testada manualmente via browser e validada com o carregamento dinâmico de múltiplas bases JSON, comprovando o correto funcionamento da interface como uma shell genérica.

---

## 7. Tratamento de Incerteza (Fatores de Certeza - MYCIN)

O sistema implementa o modelo matemático de Fatores de Certeza (CF) clássico da inteligência artificial para tratamento de informações vagas ou incompletas, operando em três etapas matemáticas:

### 7.1 Resolução dos Conectivos Lógicos (AND / OR)
Ao avaliar as premissas (condições) de uma regra, o motor combina as certezas dos fatos com base no conectivo:
* **E (AND)**: Toma o menor valor das certezas dos fatos envolvidos:
  $$CF_{premissa} = \min(CF(f_1), CF(f_2), \dots, CF(f_n))$$
* **OU (OR)**: Toma o maior valor das certezas dos fatos envolvidos:
  $$CF_{premissa} = \max(CF(f_1), CF(f_2), \dots, CF(f_n))$$

### 7.2 Propagação da Certeza pela Regra (Atenuação)
A certeza da conclusão gerada por uma única regra é o produto da certeza da premissa combinada com o peso (CF) da própria regra:
$$CF_{conclusao} = CF_{premissa} \times CF_{regra}$$

### 7.3 Acúmulo de Evidências (Combinação de Regras Independentes)
Se mais de uma regra independente apontar para a mesma conclusão diagnóstica, suas certezas são combinadas de forma acumulativa segundo a fórmula do MYCIN:
$$CF_{acumulado} = CF_1 + CF_2 - (CF_1 \times CF_2)$$
Esse modelo garante que múltiplas evidências fracas somadas fortaleçam o diagnóstico final.

---

## 8. Exemplos de Consultas Realizadas

### 8.1 Exemplo Médico (Base `diagnostico_gripe.json`)
**Objetivo**: inferir `suspeita_diagnostica`.

Entrada do usuário (resumo):
* `febre = sim`
* `tosse = sim`
* `dor_corpo = sim`
* `inicio_sintomas = subito`

Regra disparada (exemplo):
* `R02` (Gripe Influenza)

Saída esperada:
* `suspeita_diagnostica = Gripe (Influenza)` com CF calculado pelo encadeamento da regra.

Observação de explicabilidade:
* A consulta permite responder "Por quê febre foi perguntado?" e "Como suspeita_diagnostica foi obtido?", com base na trilha registrada.

### 8.2 Exemplo Automotivo (Base `diagnostico_automotivo.json`)
**Objetivo**: inferir `problema`.

Entrada do usuário (resumo):
* `luzes_painel = apagadas`

Regra disparada (exemplo):
* `R1` (Problema na Bateria)

Saída esperada:
* `problema = bateria_descarregada`.

Exemplo adicional numérico:
* Se `temperatura_motor > 110` e `direcao_dura = sim`, a regra `R6` conclui `problema = emergencia`.

### 8.3 Exemplo de Triagem UPA (Base `triagem_upa_kb.json`)
**Objetivo**: inferir, em uma única consulta, `classificacao_risco`, `hipotese_diagnostica`, `conduta_triagem`, `encaminhamento` e `orientacao_paciente`.

Entrada do usuário (resumo):
* `febre = sim`
* `prostração = sim`
* `tosse = sim`
* `dor_corpo = sim`
* `coriza = sim`
* `saturacao_o2 = 96`
* `desidratação = nao`

Principais regras disparadas (exemplo):
* `R09`: classifica risco como **AMARELO — Urgente (até 60 min)**.
* `R17`: sugere **Influenza / Síndrome Gripal**.
* `R29`: define conduta com **antitérmico + hidratação oral + repouso**.
* `R36`: encaminha para **consultório médico com prioridade amarela**.
* `R39`: orienta **isolamento respiratório e uso de máscara**.

Saída esperada (resumo):
* `classificacao_risco = AMARELO — Urgente (até 60 min)`
* `hipotese_diagnostica = Influenza / Síndrome Gripal`
* `conduta_triagem = Antitérmico (dipirona/paracetamol) + hidratação oral + repouso`
* `encaminhamento = CONSULTÓRIO MÉDICO — prioridade amarela`
* `orientacao_paciente = Use máscara; mantenha distância de outros; informe ao médico sintomas há quantos dias`

### 8.4 Exemplo de Fallback de Hipóteses
Quando uma KB não define explicitamente o campo `hypotheses`, o motor coleta automaticamente os atributos de conclusão das regras e os usa como metas.

Resultado prático:
* A consulta continua funcional sem configuração manual de hipóteses.
* O sistema mantém comportamento domain-agnostic para bases criadas livremente.

---

## 9. Limitações e Possíveis Melhorias

### 9.1 Limitações Atuais
* **Testes automatizados limitados**: a validação atual prioriza testes manuais de interface e fluxo.
* **Escalabilidade de sessão**: a abordagem por thread com espera bloqueante atende bem cenários acadêmicos, mas pode exigir ajustes para alta concorrência.
* **Conflitos semânticos de regras**: bases muito grandes podem conter regras parcialmente contraditórias, exigindo governança adicional.
* **Dependência de qualidade da KB**: perguntas ambíguas ou opções mal definidas reduzem a precisão final.
* **Integração LLM dependente de API externa**: latência, custo e disponibilidade podem afetar experiência em tempo real.

### 9.2 Melhorias Propostas
1. **Expandir suíte de testes**: incluir testes unitários para `inference_engine.py`, `explanation.py` e validações de KB.
2. **Adicionar validação estática da base**: detectar regras redundantes, ciclos, conflitos e atributos órfãos antes da execução.
3. **Aprimorar explicabilidade visual**: exportar árvore de inferência e grafo de regras no frontend.
4. **Evoluir gerenciamento de concorrência**: avaliar fila assíncrona e workers para cargas simultâneas maiores.
5. **Adicionar métricas operacionais**: tempo médio por consulta, taxa de perguntas por sessão e distribuição de CF final.
6. **Fortalecer robustez da IA**: fallback determinístico local quando o serviço externo de LLM estiver indisponível.
