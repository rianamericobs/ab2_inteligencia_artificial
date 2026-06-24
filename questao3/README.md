# ✈️ FlightBot — Assistente de Voo com IA

Sistema de assistência de voo baseado em agentes LLM usando o **Google Gemini** (API gratuita).

## 🏗️ Arquitetura

```
flight-assistant/
├── backend/
│   ├── agents.py       # Agentes LLM + ferramentas (function calling Gemini)
│   └── server.py       # API REST com FastAPI
├── frontend/
│   └── index.html      # Interface web
├── setup.py            # Script de configuração e inicialização
├── requirements.txt    # Dependências Python
└── README.md
```

## 🤖 Agentes e Ferramentas

O sistema usa **Gemini 1.5 Flash** (gratuito) com **8 ferramentas especializadas**:

| Ferramenta | Descrição |
|---|---|
| `search_flights` | Busca voos entre aeroportos |
| `get_flight_details` | Detalhes completos de um voo |
| `make_reservation` | Realiza reservas |
| `check_reservation` | Consulta reservas |
| `cancel_reservation` | Cancela reservas |
| `get_airport_info` | Informações de aeroportos |
| `check_flight_status` | Status em tempo real do voo |
| `get_baggage_rules` | Regras de bagagem por companhia |

## 🔑 Obter a chave de API (GRATUITA)

1. Acesse **[aistudio.google.com/apikey](https://aistudio.google.com/apikey)**
2. Faça login com sua conta Google
3. Clique em **"Create API Key"**
4. Copie a chave gerada

> O plano gratuito inclui 15 requisições/minuto e 1 milhão de tokens/dia com o Gemini 1.5 Flash — mais do que suficiente para uso normal.

## 🚀 Como executar

### Passo 1 — Configurar a chave de API

**Linux/macOS:**
```bash
export GEMINI_API_KEY="AIza..."
```

**Windows (CMD):**
```cmd
set GEMINI_API_KEY=AIza...
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY = "AIza..."
```

### Passo 2 — Executar

```bash
python setup.py
```

O script irá:
1. Verificar o Python
2. Instalar as dependências automaticamente
3. Iniciar o servidor em `http://localhost:8000`
4. Abrir o frontend no navegador

### Alternativa — Execução manual

```bash
pip install -r requirements.txt
python backend/server.py
# Abra frontend/index.html no navegador
```

### Modo terminal (sem interface web)

```bash
python backend/agents.py
```

## 💬 Exemplos de uso

```
Você: Quero voos de GRU para BSB para amanhã, 2 passageiros
Você: Quero reservar o voo LA3100 para João Silva, CPF 123.456.789-00
Você: Consultar reserva BR123456
Você: Status do voo G31234 hoje?
Você: Regras de bagagem da GOL econômica
Você: Informações sobre o aeroporto de Fortaleza
Você: Cancelar reserva BR123456
```

## ⚙️ Customização

### Trocar o modelo Gemini

Em `backend/agents.py`, linha do `GenerativeModel`:

```python
# Opções gratuitas:
model_name="gemini-1.5-flash"    # rápido, padrão
model_name="gemini-1.5-flash-8b" # mais leve ainda
model_name="gemini-1.5-pro"      # mais capaz (limite menor)
```

### Adicionar novos voos

Em `backend/agents.py`, edite o dicionário `FLIGHTS_DB`.

### Endpoints da API

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/` | Status |
| `POST` | `/chat` | Enviar mensagem |
| `POST` | `/session/new` | Nova sessão |
| `DELETE` | `/session/{id}` | Limpar sessão |

Documentação interativa: `http://localhost:8000/docs`
