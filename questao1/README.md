# K-RuleShell — Sistema Especialista Genérico

Uma shell genérica e moderna para construção de **Sistemas Baseados em Conhecimento** voltados a tarefas de diagnóstico, classificação e recomendação de ações. O sistema opera tanto em interface de terminal (CLI) quanto em um painel web moderno (HTML/CSS + FastAPI), sendo 100% agnóstico a domínios de conhecimento.

---

##  Funcionalidades Principais

* **Motor de Inferência Triplo**: Suporte a encadeamento para frente (Forward Chaining), encadeamento para trás (Backward Chaining) e estratégia híbrida otimizada para consultas interativas.
* **Mecanismo de Explicação Completo**: Respostas às perguntas de explicação lógica estruturada (explicando **Por quê?** uma pergunta é feita e **Como?** um fato foi concluído) e geração de narrativas fluidas em linguagem natural integrada via IA.
* **Validação de Limites Genérica**: Validação robusta de respostas livres baseada em intervalos numéricos (`min` e `max`) definidos dinamicamente na base de conhecimento.
* **Assistente Inteligente (IA)**: Cadastro rápido e em lote de regras de produção e perguntas/metadados enviando descrições em linguagem natural.
* **Interface Web Premium**: Dashboard completo e clean (visual escuro slate/indigo) em FastAPI, HTML, CSS e JavaScript que opera como uma shell gráfica para carregar e gerenciar qualquer base de conhecimento JSON.

---

##  Como Executar

### Pré-requisitos
Instale as dependências necessárias:
```bash
pip install -r requirements.txt

Adicione a raiz do projeto um arquivo .env com a seguinte chave:
GROQ_API_KEY="sua_chave_aqui"
Ou
API_KEY="sua_chave_aqui"
```

```bash
# Navegue até a raiz do projeto:
cd questao1
```

### 1. Interface Web (FastAPI + Dashboard)
Inicie o servidor uvicorn local:
```bash
fastapi dev .\web\server.py
```
Acesse **`http://127.0.0.1:8000`** no seu navegador para carregar bases JSON, fazer uploads, rodar consultas interativas visualmente, ver explicações geradas por IA e editar regras.

### 2. Interface de Terminal (CLI)
Inicie a CLI interativa:
```bash
# Iniciar shell genérica vazia
python main.py

# Iniciar carregando a demonstração de triagem médica
python main.py demos/triagem_upa_kb.json
```

---

## Estrutura do Projeto

```
questao1/
├── core/
│   ├── knowledge_base.py     → Representação de Fatos, Regras, Condições e serialização JSON
│   ├── inference_engine.py   → Algoritmos Forward, Backward e Híbrido com fallback de hipóteses
│   ├── explanation.py        → Mecanismo formal de explicação (Why/How)
│   ├── kb_editor.py          → Manipulador interativo das bases de dados no terminal
│   └── llm_client.py         → Integração Groq para tradução de explicações e parsing de linguagem natural
├── ui/
│   └── cli.py                → Shell interativa do terminal
├── web/
│   ├── server.py             → Servidor FastAPI com session manager multi-threaded
│   └── static/               → Arquivos estáticos da interface web (HTML, CSS e JS)
├── demos/
│   └── triagem_upa_kb.json   → Base de demonstração clínica com regras e intervalos
└── main.py                   # Ponto de entrada do console CLI
```
