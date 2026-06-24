"""
Flight Assistant - Multi-Agent System
Agentes especializados para assistência de voo usando Google Gemini API (gratuita)
"""

import json
import os
import google.generativeai as genai
from datetime import datetime
import random

# Configura o cliente Gemini com a chave de API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

# ─────────────────────────────────────────────
# DADOS SIMULADOS (substitua por APIs reais)
# ─────────────────────────────────────────────

FLIGHTS_DB = {
    "GRU-CGH": [
        {"flight": "LA3050", "dep": "06:00", "arr": "06:55", "price": 189, "seats": 12, "airline": "LATAM"},
        {"flight": "G31234", "dep": "08:30", "arr": "09:25", "price": 145, "seats": 3, "airline": "GOL"},
        {"flight": "AD4567", "dep": "12:00", "arr": "12:55", "price": 210, "seats": 28, "airline": "Azul"},
        {"flight": "LA3052", "dep": "18:00", "arr": "18:55", "price": 175, "seats": 7, "airline": "LATAM"},
    ],
    "CGH-GRU": [
        {"flight": "LA3051", "dep": "07:30", "arr": "08:25", "price": 195, "seats": 15, "airline": "LATAM"},
        {"flight": "G31235", "dep": "10:00", "arr": "10:55", "price": 162, "seats": 2, "airline": "GOL"},
    ],
    "GRU-BSB": [
        {"flight": "LA3100", "dep": "07:00", "arr": "08:30", "price": 320, "seats": 20, "airline": "LATAM"},
        {"flight": "G35678", "dep": "11:00", "arr": "12:30", "price": 285, "seats": 8, "airline": "GOL"},
        {"flight": "AD8901", "dep": "16:00", "arr": "17:30", "price": 298, "seats": 14, "airline": "Azul"},
    ],
    "BSB-GRU": [
        {"flight": "LA3101", "dep": "09:00", "arr": "10:30", "price": 310, "seats": 18, "airline": "LATAM"},
        {"flight": "G35679", "dep": "14:00", "arr": "15:30", "price": 275, "seats": 6, "airline": "GOL"},
    ],
    "GRU-FOR": [
        {"flight": "LA3200", "dep": "08:00", "arr": "11:30", "price": 450, "seats": 5, "airline": "LATAM"},
        {"flight": "G37890", "dep": "13:00", "arr": "16:30", "price": 398, "seats": 11, "airline": "GOL"},
    ],
    "REC-SSA": [
        {"flight": "LA4001", "dep": "09:00", "arr": "10:10", "price": 220, "seats": 9, "airline": "LATAM"},
        {"flight": "G34001", "dep": "15:00", "arr": "16:10", "price": 195, "seats": 4, "airline": "GOL"},
    ],
}

AIRPORTS = {
    "GRU": {"name": "Aeroporto Internacional de Guarulhos", "city": "São Paulo", "state": "SP"},
    "CGH": {"name": "Aeroporto de Congonhas", "city": "São Paulo", "state": "SP"},
    "BSB": {"name": "Aeroporto Internacional de Brasília", "city": "Brasília", "state": "DF"},
    "FOR": {"name": "Aeroporto Internacional Pinto Martins", "city": "Fortaleza", "state": "CE"},
    "REC": {"name": "Aeroporto Internacional do Recife", "city": "Recife", "state": "PE"},
    "SSA": {"name": "Aeroporto Internacional de Salvador", "city": "Salvador", "state": "BA"},
    "POA": {"name": "Aeroporto Internacional Salgado Filho", "city": "Porto Alegre", "state": "RS"},
    "CWB": {"name": "Aeroporto Internacional Afonso Pena", "city": "Curitiba", "state": "PR"},
    "MAO": {"name": "Aeroporto Internacional Eduardo Gomes", "city": "Manaus", "state": "AM"},
    "BEL": {"name": "Aeroporto Internacional Val-de-Cans", "city": "Belém", "state": "PA"},
    "MCZ": {"name": "Aeroporto Internacional Zumbi dos Palmares", "city": "Maceió", "state": "AL"},
}

RESERVATIONS = {}  # Armazena reservas em memória

# ─────────────────────────────────────────────
# FERRAMENTAS DOS AGENTES
# ─────────────────────────────────────────────

def search_flights(origin: str, destination: str, date: str, passengers: int = 1) -> dict:
    """Busca voos disponíveis entre origem e destino."""
    key = f"{origin.upper()}-{destination.upper()}"
    flights = FLIGHTS_DB.get(key, [])
    
    if not flights:
        return {
            "status": "not_found",
            "message": f"Nenhum voo direto encontrado de {origin} para {destination}.",
            "suggestion": "Tente uma rota com conexão ou datas alternativas."
        }
    
    available = []
    for f in flights:
        if f["seats"] >= passengers:
            total = f["price"] * passengers
            available.append({
                **f,
                "passengers": passengers,
                "total_price": total,
                "date": date,
                "route": key,
                "seats_available": f["seats"],
                "status": "disponível"
            })
    
    if not available:
        return {
            "status": "no_seats",
            "message": f"Voos encontrados, mas sem assentos suficientes para {passengers} passageiro(s).",
        }
    
    return {
        "status": "success",
        "origin": AIRPORTS.get(origin.upper(), {"city": origin}),
        "destination": AIRPORTS.get(destination.upper(), {"city": destination}),
        "date": date,
        "passengers": passengers,
        "flights": available,
        "count": len(available)
    }


def get_flight_details(flight_code: str) -> dict:
    """Retorna detalhes completos de um voo específico."""
    for key, flights in FLIGHTS_DB.items():
        for f in flights:
            if f["flight"].upper() == flight_code.upper():
                origin, dest = key.split("-")
                return {
                    "status": "success",
                    "flight": f["flight"],
                    "airline": f["airline"],
                    "origin": AIRPORTS.get(origin, {"city": origin, "name": origin}),
                    "destination": AIRPORTS.get(dest, {"city": dest, "name": dest}),
                    "departure": f["dep"],
                    "arrival": f["arr"],
                    "price_per_person": f["price"],
                    "seats_available": f["seats"],
                    "baggage": "1 bagagem de mão (10kg) + 1 despachada (23kg)",
                    "meal": "Disponível para compra a bordo",
                    "refundable": True if f["price"] > 200 else False,
                    "class": "Econômica"
                }
    return {"status": "not_found", "message": f"Voo {flight_code} não encontrado."}


def make_reservation(flight_code: str, passenger_name: str, passenger_cpf: str, 
                     date: str, passengers: int = 1, seat_preference: str = "qualquer") -> dict:
    """Realiza uma reserva de voo."""
    # Busca o voo
    flight_info = get_flight_details(flight_code)
    if flight_info["status"] == "not_found":
        return {"status": "error", "message": f"Voo {flight_code} não encontrado."}
    
    if flight_info["seats_available"] < passengers:
        return {"status": "error", "message": "Assentos insuficientes para o número de passageiros."}
    
    # Gera código de reserva
    reservation_code = f"BR{random.randint(100000, 999999)}"
    seat_number = f"{random.randint(1, 35)}{random.choice(['A','B','C','D','E','F'])}"
    
    reservation = {
        "reservation_code": reservation_code,
        "flight": flight_code,
        "airline": flight_info["airline"],
        "passenger_name": passenger_name,
        "passenger_cpf": passenger_cpf,
        "date": date,
        "departure": flight_info["departure"],
        "arrival": flight_info["arrival"],
        "origin": flight_info["origin"],
        "destination": flight_info["destination"],
        "passengers": passengers,
        "seat": seat_number,
        "seat_preference": seat_preference,
        "total_price": flight_info["price_per_person"] * passengers,
        "status": "confirmada",
        "created_at": datetime.now().isoformat(),
        "baggage": flight_info["baggage"],
    }
    
    RESERVATIONS[reservation_code] = reservation
    return {"status": "success", "reservation": reservation}


def check_reservation(reservation_code: str) -> dict:
    """Consulta uma reserva existente."""
    res = RESERVATIONS.get(reservation_code.upper())
    if res:
        return {"status": "success", "reservation": res}
    return {
        "status": "not_found", 
        "message": f"Reserva {reservation_code} não encontrada. Verifique o código."
    }


def cancel_reservation(reservation_code: str, reason: str = "") -> dict:
    """Cancela uma reserva."""
    res = RESERVATIONS.get(reservation_code.upper())
    if not res:
        return {"status": "not_found", "message": f"Reserva {reservation_code} não encontrada."}
    
    if res["status"] == "cancelada":
        return {"status": "already_cancelled", "message": "Esta reserva já foi cancelada."}
    
    RESERVATIONS[reservation_code]["status"] = "cancelada"
    RESERVATIONS[reservation_code]["cancelled_at"] = datetime.now().isoformat()
    RESERVATIONS[reservation_code]["cancel_reason"] = reason
    
    refund = res["total_price"] * 0.8  # 80% de reembolso
    return {
        "status": "success",
        "message": f"Reserva {reservation_code} cancelada com sucesso.",
        "refund_amount": refund,
        "refund_info": "O reembolso de R$ {:.2f} será processado em até 7 dias úteis.".format(refund)
    }


def get_airport_info(airport_code: str) -> dict:
    """Retorna informações sobre um aeroporto."""
    info = AIRPORTS.get(airport_code.upper())
    if info:
        # Adiciona informações extras simuladas
        return {
            "status": "success",
            "code": airport_code.upper(),
            **info,
            "terminals": random.randint(1, 3),
            "facilities": ["Lounge VIP", "Wi-Fi gratuito", "Lanchonetes", "Farmácia", "Câmbio"],
            "check_in_online": "Disponível 48h antes do voo",
            "check_in_airport": "Recomendado 2h antes para voos domésticos",
            "taxi_to_center": f"~{random.randint(15, 45)} min de táxi",
        }
    return {"status": "not_found", "message": f"Aeroporto {airport_code} não encontrado."}


def check_flight_status(flight_code: str, date: str) -> dict:
    """Verifica o status atual de um voo."""
    flight_info = get_flight_details(flight_code)
    if flight_info["status"] == "not_found":
        return flight_info
    
    # Simula status aleatório
    statuses = [
        {"status": "no_horario", "label": "No Horário", "delay": 0},
        {"status": "atrasado", "label": "Atrasado", "delay": random.randint(15, 120)},
        {"status": "embarcando", "label": "Embarcando", "delay": 0},
        {"status": "pousou", "label": "Pousou", "delay": 0},
    ]
    current = random.choice(statuses)
    
    return {
        "status": "success",
        "flight": flight_code,
        "date": date,
        "scheduled_departure": flight_info["departure"],
        "scheduled_arrival": flight_info["arrival"],
        "flight_status": current["label"],
        "delay_minutes": current.get("delay", 0),
        "gate": f"Gate {random.randint(1, 30)}{random.choice(['A','B','C',''])}",
        "terminal": f"Terminal {random.randint(1, 3)}",
    }


def get_baggage_rules(airline: str, ticket_type: str = "economica") -> dict:
    """Retorna regras de bagagem de uma companhia aérea."""
    rules = {
        "LATAM": {
            "economica": {
                "carry_on": "1 peça até 10kg",
                "checked": "1 peça de 23kg incluída",
                "extra_bag": "R$ 150 por bagagem adicional",
                "oversize": "R$ 200 para bagagens acima de 23kg"
            }
        },
        "GOL": {
            "economica": {
                "carry_on": "1 peça até 10kg",
                "checked": "Não incluída – a partir de R$ 70",
                "extra_bag": "R$ 130 por bagagem adicional",
                "oversize": "R$ 180 para bagagens acima de 23kg"
            }
        },
        "Azul": {
            "economica": {
                "carry_on": "1 peça até 10kg",
                "checked": "1 peça de 23kg incluída",
                "extra_bag": "R$ 140 por bagagem adicional",
                "oversize": "R$ 190 para bagagens acima de 23kg"
            }
        }
    }
    
    airline_rules = rules.get(airline, rules.get("LATAM"))
    ticket_rules = airline_rules.get(ticket_type, airline_rules.get("economica"))
    
    return {
        "status": "success",
        "airline": airline,
        "ticket_type": ticket_type,
        "rules": ticket_rules,
        "tips": [
            "Liquidos em recipientes de até 100ml devem ir em saco plástico transparente",
            "Itens proibidos: armas, líquidos inflamáveis, baterias de lítio extras",
            "Faça o check-in online para agilizar o processo no aeroporto"
        ]
    }


# ─────────────────────────────────────────────
# DEFINIÇÃO DOS TOOLS PARA A API GEMINI
# ─────────────────────────────────────────────

TOOLS = [
    genai.protos.Tool(
        function_declarations=[
            genai.protos.FunctionDeclaration(
                name="search_flights",
                description="Busca voos disponíveis entre dois aeroportos em uma data específica. Use códigos IATA (ex: GRU, CGH, BSB, FOR, REC, SSA).",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "origin": genai.protos.Schema(type=genai.protos.Type.STRING, description="Código IATA do aeroporto de origem (ex: GRU)"),
                        "destination": genai.protos.Schema(type=genai.protos.Type.STRING, description="Código IATA do aeroporto de destino (ex: BSB)"),
                        "date": genai.protos.Schema(type=genai.protos.Type.STRING, description="Data do voo no formato DD/MM/YYYY"),
                        "passengers": genai.protos.Schema(type=genai.protos.Type.INTEGER, description="Número de passageiros (padrão: 1)"),
                    },
                    required=["origin", "destination", "date"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="get_flight_details",
                description="Retorna informações detalhadas de um voo específico pelo código do voo.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "flight_code": genai.protos.Schema(type=genai.protos.Type.STRING, description="Código do voo (ex: LA3050, G31234)"),
                    },
                    required=["flight_code"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="make_reservation",
                description="Realiza uma reserva de voo para um passageiro.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "flight_code": genai.protos.Schema(type=genai.protos.Type.STRING, description="Código do voo"),
                        "passenger_name": genai.protos.Schema(type=genai.protos.Type.STRING, description="Nome completo do passageiro"),
                        "passenger_cpf": genai.protos.Schema(type=genai.protos.Type.STRING, description="CPF do passageiro"),
                        "date": genai.protos.Schema(type=genai.protos.Type.STRING, description="Data do voo"),
                        "passengers": genai.protos.Schema(type=genai.protos.Type.INTEGER, description="Número de passageiros"),
                        "seat_preference": genai.protos.Schema(type=genai.protos.Type.STRING, description="Preferência de assento: janela, corredor ou qualquer"),
                    },
                    required=["flight_code", "passenger_name", "passenger_cpf", "date"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="check_reservation",
                description="Consulta os detalhes de uma reserva existente pelo código de reserva.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "reservation_code": genai.protos.Schema(type=genai.protos.Type.STRING, description="Código da reserva (ex: BR123456)"),
                    },
                    required=["reservation_code"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="cancel_reservation",
                description="Cancela uma reserva de voo existente.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "reservation_code": genai.protos.Schema(type=genai.protos.Type.STRING, description="Código da reserva a cancelar"),
                        "reason": genai.protos.Schema(type=genai.protos.Type.STRING, description="Motivo do cancelamento (opcional)"),
                    },
                    required=["reservation_code"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="get_airport_info",
                description="Retorna informações sobre um aeroporto brasileiro: terminal, facilidades, dicas de check-in.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "airport_code": genai.protos.Schema(type=genai.protos.Type.STRING, description="Código IATA do aeroporto (ex: GRU, CGH)"),
                    },
                    required=["airport_code"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="check_flight_status",
                description="Verifica o status atual de um voo: no horário, atrasado, embarcando, etc.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "flight_code": genai.protos.Schema(type=genai.protos.Type.STRING, description="Código do voo"),
                        "date": genai.protos.Schema(type=genai.protos.Type.STRING, description="Data do voo"),
                    },
                    required=["flight_code", "date"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="get_baggage_rules",
                description="Retorna as regras de bagagem de uma companhia aérea.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "airline": genai.protos.Schema(type=genai.protos.Type.STRING, description="Nome da companhia aérea (LATAM, GOL, Azul)"),
                        "ticket_type": genai.protos.Schema(type=genai.protos.Type.STRING, description="Tipo da passagem: economica, executiva"),
                    },
                    required=["airline"]
                )
            ),
        ]
    )
]

# Mapeamento de funções
TOOL_FUNCTIONS = {
    "search_flights": search_flights,
    "get_flight_details": get_flight_details,
    "make_reservation": make_reservation,
    "check_reservation": check_reservation,
    "cancel_reservation": cancel_reservation,
    "get_airport_info": get_airport_info,
    "check_flight_status": check_flight_status,
    "get_baggage_rules": get_baggage_rules,
}

# ─────────────────────────────────────────────
# SISTEMA DE AGENTES
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# SISTEMA DE AGENTES COM GEMINI
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """Você é o FlightBot, um assistente virtual especializado em viagens aéreas no Brasil. 
Você tem acesso a ferramentas para:
- 🔍 Buscar voos disponíveis
- ✈️ Verificar detalhes e status de voos
- 📋 Fazer, consultar e cancelar reservas
- 🏛️ Informar sobre aeroportos
- 🧳 Esclarecer regras de bagagem

**Aeroportos disponíveis:** GRU (São Paulo/Guarulhos), CGH (São Paulo/Congonhas), BSB (Brasília), 
FOR (Fortaleza), REC (Recife), SSA (Salvador), POA (Porto Alegre), CWB (Curitiba), MAO (Manaus), 
BEL (Belém), MCZ (Maceió)

**Comportamento:**
- Seja amigável, prestativo e profissional em português brasileiro
- Sempre confirme as informações antes de realizar ações como reservas ou cancelamentos
- Formate valores em Reais (R$) e datas no padrão brasileiro (DD/MM/YYYY)
- Quando buscar voos, apresente as opções de forma clara e organizada
- Sugira alternativas quando não encontrar o que o usuário pediu
- Para reservas, sempre confirme os dados do passageiro antes de prosseguir

Hoje é: """ + datetime.now().strftime("%d/%m/%Y")


def run_agent(user_message: str, conversation_history: list) -> tuple[str, list]:
    """
    Executa o agente Gemini com suporte a múltiplos turnos de function calling.
    O histórico usa o formato nativo do Gemini SDK.
    Retorna (resposta_final, histórico_atualizado)
    """
    # Cria o modelo com instruções de sistema e ferramentas
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",   # gratuito e rápido
        system_instruction=SYSTEM_PROMPT,
        tools=TOOLS,
    )

    # Inicia (ou retoma) o chat com o histórico existente
    chat = model.start_chat(history=conversation_history)

    # Envia a mensagem do usuário
    response = chat.send_message(user_message)

    # Loop de function calling — o Gemini pode chamar múltiplas ferramentas
    while True:
        # Coleta todas as function calls desta rodada
        fn_calls = []
        for part in response.parts:
            if part.function_call.name:
                fn_calls.append(part.function_call)

        if not fn_calls:
            # Nenhuma ferramenta chamada → resposta final em texto
            break

        # Executa cada função e monta as respostas
        fn_responses = []
        for fn_call in fn_calls:
            tool_name = fn_call.name
            tool_args = dict(fn_call.args)

            if tool_name in TOOL_FUNCTIONS:
                try:
                    result = TOOL_FUNCTIONS[tool_name](**tool_args)
                except Exception as e:
                    result = {"status": "error", "message": str(e)}
            else:
                result = {"status": "error", "message": f"Ferramenta '{tool_name}' não encontrada."}

            fn_responses.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=tool_name,
                        response={"result": json.dumps(result, ensure_ascii=False)}
                    )
                )
            )

        # Devolve os resultados ao modelo
        response = chat.send_message(fn_responses)

    # Extrai texto da resposta final
    final_text = response.text if hasattr(response, "text") else ""
    if not final_text:
        for part in response.parts:
            if hasattr(part, "text") and part.text:
                final_text = part.text
                break

    # Atualiza o histórico com o estado atual do chat
    updated_history = chat.history

    return final_text or "Desculpe, não consegui processar sua solicitação.", updated_history


if __name__ == "__main__":
    print("🛫 FlightBot - Assistente de Voo")
    print("=" * 50)
    print("Digite 'sair' para encerrar\n")
    
    history = []
    while True:
        user_input = input("Você: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["sair", "exit", "quit"]:
            print("FlightBot: Até logo! Boas viagens! ✈️")
            break
        
        response, history = run_agent(user_input, history)
        print(f"\nFlightBot: {response}\n")
