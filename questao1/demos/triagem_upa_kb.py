"""
Base de Conhecimento: Triagem Ambulatorial — UPA / UBS / Posto de Saúde
Cobre: Gripe/Influenza, Síndrome Gripal, COVID-19, Diarreia/Gastroenterite,
       Hipertensão Crise, Infecção Urinária, Amigdalite, Dengue,
       Desidratação, Crise Asmática
≥ 20 regras | ≥ 30 fatos | ≥ 5 hipóteses
Baseado em: Protocolo de Manchester adaptado + PCDT/MS Brasil
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.knowledge_base import KnowledgeBase
from core.kb_editor import KBEditor


def build_triagem_kb() -> KnowledgeBase:
    kb = KnowledgeBase(
        domain="triagem_ambulatorial",
        description=(
            "Sistema de triagem ambulatorial para UPA/UBS. "
            "Auxilia na classificação de risco e direcionamento do paciente. "
            "NÃO substitui avaliação médica."
        )
    )
    ed = KBEditor(kb)

    # ── Hipóteses que o sistema tenta resolver ─────────────────────────────
    kb.hypotheses = [
        "classificacao_risco",   # Azul / Verde / Amarelo / Laranja / Vermelho
        "hipotese_diagnostica",  # diagnóstico provável
        "conduta_triagem",       # o que fazer agora
        "encaminhamento",        # onde o paciente deve ir
        "orientacao_paciente",   # orientações gerais
    ]

    # ── Perguntas ao usuário (atributo, texto, opções) ─────────────────────
    perguntas = {
        # Sinais Vitais
        "temperatura": (
            "Qual a temperatura axilar do paciente (°C)? [ex: 37.8]", None),
        "saturacao_o2": (
            "Qual a saturação de O₂ (%)? [ex: 96]", None),
        "pressao_sistolica": (
            "Qual a pressão arterial sistólica (mmHg)? [ex: 140]", None),
        "pressao_diastolica": (
            "Qual a pressão arterial diastólica (mmHg)? [ex: 90]", None),
        "frequencia_cardiaca": (
            "Qual a frequência cardíaca (bpm)? [ex: 88]", None),
        "frequencia_respiratoria": (
            "Qual a frequência respiratória (irpm)? [ex: 18]", None),
        "glicemia_capilar": (
            "Qual a glicemia capilar (mg/dL)? [ex: 120]", None),

        # Sintomas Gerais
        "febre": (
            "O paciente tem febre (temperatura ≥ 37,8°C)?", ["sim", "nao"]),
        "tosse": (
            "O paciente tem tosse?", ["sim", "seca", "produtiva", "nao"]),
        "dor_garganta": (
            "Há dor de garganta?", ["sim", "nao"]),
        "coriza": (
            "Há coriza ou obstrução nasal?", ["sim", "nao"]),
        "dor_cabeca": (
            "Há cefaleia (dor de cabeça)?", ["sim", "nao"]),
        "dor_corpo": (
            "Há mialgia (dor no corpo)?", ["sim", "nao"]),
        "prostração": (
            "Há prostração intensa / cansaço extremo?", ["sim", "nao"]),
        "falta_ar": (
            "Há dispneia (falta de ar)?", ["sim", "moderada", "grave", "nao"]),
        "chiado_peito": (
            "Há sibilância (chiado no peito)?", ["sim", "nao"]),
        "dor_toracica": (
            "Há dor torácica?", ["sim", "nao"]),
        "náusea_vomito": (
            "Há náusea ou vômito?", ["sim", "nao"]),
        "diarreia": (
            "Há diarreia? Quantas evacuações nas últimas 24h?",
            ["nao", "1-3", "4-6", "mais_de_6"]),
        "sangue_fezes": (
            "Há sangue nas fezes (hematoquezia)?", ["sim", "nao"]),
        "dor_abdominal": (
            "Há dor abdominal?", ["sim", "cólica", "difusa", "nao"]),
        "desidratação": (
            "Há sinais de desidratação (boca seca, olhos fundos, sem urina)?",
            ["nao", "leve", "moderada", "grave"]),
        "dor_lombar_flanco": (
            "Há dor lombar ou em flanco?", ["sim", "nao"]),
        "disuria": (
            "Há ardência/dor ao urinar (disúria)?", ["sim", "nao"]),
        "polaciuria": (
            "Há aumento da frequência urinária (polaciúria)?", ["sim", "nao"]),
        "urina_turva": (
            "A urina está turva ou com odor fétido?", ["sim", "nao"]),
        "dor_olhos": (
            "Há dor retroocular (atrás dos olhos)?", ["sim", "nao"]),
        "manchas_pele": (
            "Há manchas/exantema na pele?", ["sim", "petequias", "maculopapular", "nao"]),
        "sangramento_espontaneo": (
            "Há sangramento espontâneo (gengiva, nariz, pele)?", ["sim", "nao"]),
        "dor_articular": (
            "Há artralgia/arthrite (dor nas articulações)?", ["sim", "nao"]),
        "amigdalas_exsudato": (
            "Há exsudato (pus) nas amígdalas?", ["sim", "nao"]),
        "rigidez_nuca": (
            "Há rigidez de nuca?", ["sim", "nao"]),
        "nivel_consciencia": (
            "Qual o nível de consciência do paciente?",
            ["alerta", "confuso", "sonolento", "inconsciente"]),
        "historico_hipertensao": (
            "O paciente tem diagnóstico prévio de hipertensão arterial?", ["sim", "nao"]),
        "historico_asma": (
            "O paciente tem diagnóstico de asma ou DPOC?", ["sim", "nao"]),
        "uso_broncodilatador": (
            "Já usou broncodilatador hoje sem melhora?", ["sim", "nao"]),
        "gravidez": (
            "A paciente está grávida ou pode estar grávida?", ["sim", "nao", "nao_aplicavel"]),
        "criança_menor_5": (
            "O paciente é criança menor de 5 anos?", ["sim", "nao"]),
        "idoso_maior_60": (
            "O paciente tem mais de 60 anos?", ["sim", "nao"]),
        "contato_dengue": (
            "Há relato de contato com casos de dengue ou mora em área endêmica?",
            ["sim", "nao"]),
    }

    for attr, (question, options) in perguntas.items():
        kb.register_question(attr, question, options)

    # Limites clínicos para os sinais vitais
    ranges = {
        "temperatura": (30.0, 45.0),
        "saturacao_o2": (0.0, 100.0),
        "pressao_sistolica": (20.0, 300.0),
        "pressao_diastolica": (10.0, 200.0),
        "frequencia_cardiaca": (10.0, 300.0),
        "frequencia_respiratoria": (2.0, 80.0),
        "glicemia_capilar": (10.0, 1000.0),
    }
    for attr, (min_val, max_val) in ranges.items():
        kb.register_attribute_range(attr, min_val, max_val)

    # ══════════════════════════════════════════════════════════════════
    # BLOCO 1 — CLASSIFICAÇÃO DE RISCO (Protocolo Manchester adaptado)
    # ══════════════════════════════════════════════════════════════════

    # VERMELHO — Emergência imediata
    ed.add_rule_programmatic(
        "R01", "VERMELHO — Saturação crítica",
        [("saturacao_o2", "<", "90")],
        ("classificacao_risco", "VERMELHO — Emergência (atendimento imediato)"),
        priority=20,
        description="SpO2 < 90% — risco iminente de vida"
    )
    ed.add_rule_programmatic(
        "R02", "VERMELHO — Crise hipertensiva grave",
        [("pressao_sistolica", ">", "180"), ("nivel_consciencia", "!=", "alerta")],
        ("classificacao_risco", "VERMELHO — Emergência (atendimento imediato)"),
        priority=20,
        description="PAS > 180 + alteração de consciência — emergência hipertensiva"
    )
    ed.add_rule_programmatic(
        "R03", "VERMELHO — Inconsciência",
        [("nivel_consciencia", "=", "inconsciente")],
        ("classificacao_risco", "VERMELHO — Emergência (atendimento imediato)"),
        priority=20,
        description="Paciente inconsciente — Glasgow < 9"
    )
    ed.add_rule_programmatic(
        "R04", "VERMELHO — Rigidez de nuca",
        [("rigidez_nuca", "=", "sim"), ("febre", "=", "sim")],
        ("classificacao_risco", "VERMELHO — Emergência (atendimento imediato)"),
        priority=20,
        description="Febre + rigidez de nuca — suspeita de meningite"
    )

    # LARANJA — Muito urgente (≤ 10 min)
    ed.add_rule_programmatic(
        "R05", "LARANJA — Dispneia grave",
        [("falta_ar", "=", "grave"), ("saturacao_o2", "<", "94")],
        ("classificacao_risco", "LARANJA — Muito Urgente (até 10 min)"),
        priority=18,
        description="Insuficiência respiratória moderada-grave"
    )
    ed.add_rule_programmatic(
        "R06", "LARANJA — Crise hipertensiva sintomática",
        [("pressao_sistolica", ">", "180"), ("dor_cabeca", "=", "sim")],
        ("classificacao_risco", "LARANJA — Muito Urgente (até 10 min)"),
        priority=18,
        description="PAS > 180 com cefaleia — urgência hipertensiva"
    )
    ed.add_rule_programmatic(
        "R07", "LARANJA — Desidratação grave",
        [("desidratação", "=", "grave"), ("nivel_consciencia", "!=", "alerta")],
        ("classificacao_risco", "LARANJA — Muito Urgente (até 10 min)"),
        priority=18,
        description="Desidratação grave com rebaixamento"
    )
    ed.add_rule_programmatic(
        "R08", "LARANJA — Dengue com sinais de alarme",
        [("sangramento_espontaneo", "=", "sim"), ("manchas_pele", "=", "petequias")],
        ("classificacao_risco", "LARANJA — Muito Urgente (até 10 min)"),
        priority=18,
        description="Dengue com sinais de alarme — risco de dengue grave"
    )

    # AMARELO — Urgente (≤ 60 min)
    ed.add_rule_programmatic(
        "R09", "AMARELO — Síndrome febril + prostração",
        [("febre", "=", "sim"), ("prostração", "=", "sim")],
        ("classificacao_risco", "AMARELO — Urgente (até 60 min)"),
        priority=15,
        description="Febre alta com comprometimento do estado geral"
    )
    ed.add_rule_programmatic(
        "R10", "AMARELO — Diarreia intensa com desidratação",
        [("diarreia", "=", "mais_de_6"), ("desidratação", "=", "moderada")],
        ("classificacao_risco", "AMARELO — Urgente (até 60 min)"),
        priority=15,
        description="Diarreia grave com desidratação moderada"
    )
    ed.add_rule_programmatic(
        "R11", "AMARELO — Crise asmática moderada",
        [("chiado_peito", "=", "sim"), ("falta_ar", "=", "moderada"), ("uso_broncodilatador", "=", "sim")],
        ("classificacao_risco", "AMARELO — Urgente (até 60 min)"),
        priority=15,
        description="Asma sem resposta ao broncodilatador"
    )
    ed.add_rule_programmatic(
        "R12", "AMARELO — Gestante febril",
        [("gravidez", "=", "sim"), ("febre", "=", "sim")],
        ("classificacao_risco", "AMARELO — Urgente (até 60 min)"),
        priority=16,
        description="Febre em gestante — risco para feto"
    )

    # VERDE — Pouco urgente (≤ 120 min)
    ed.add_rule_programmatic(
        "R13", "VERDE — Quadro gripal leve",
        [("febre", "=", "sim"), ("tosse", "=", "sim"),
         ("saturacao_o2", ">=", "95"), ("prostração", "=", "nao")],
        ("classificacao_risco", "VERDE — Pouco Urgente (até 2h)"),
        priority=10,
        description="Síndrome gripal sem comprometimento respiratório"
    )
    ed.add_rule_programmatic(
        "R14", "VERDE — ITU simples",
        [("disuria", "=", "sim"), ("polaciuria", "=", "sim"), ("febre", "=", "nao")],
        ("classificacao_risco", "VERDE — Pouco Urgente (até 2h)"),
        priority=10,
        description="ITU baixa sem febre — cistite simples"
    )
    ed.add_rule_programmatic(
        "R15", "VERDE — Diarreia leve sem desidratação",
        [("diarreia", "=", "1-3"), ("desidratação", "=", "nao")],
        ("classificacao_risco", "VERDE — Pouco Urgente (até 2h)"),
        priority=10,
        description="Gastroenterite leve, hidratado"
    )

    # AZUL — Não urgente (ordem de chegada)
    ed.add_rule_programmatic(
        "R16", "AZUL — Queixa leve sem febre",
        [("febre", "=", "nao"), ("falta_ar", "=", "nao"),
         ("nivel_consciencia", "=", "alerta"), ("pressao_sistolica", "<", "160")],
        ("classificacao_risco", "AZUL — Não Urgente (ordem de chegada)"),
        priority=5,
        description="Queixa menor, estável, sem risco identificado"
    )

    # ══════════════════════════════════════════════════════════════════
    # BLOCO 2 — HIPÓTESE DIAGNÓSTICA
    # ══════════════════════════════════════════════════════════════════

    ed.add_rule_programmatic(
        "R17", "Hipótese: Influenza / Síndrome Gripal",
        [("febre", "=", "sim"), ("tosse", "=", "sim"),
         ("dor_corpo", "=", "sim"), ("coriza", "=", "sim")],
        ("hipotese_diagnostica", "Influenza / Síndrome Gripal"),
        priority=12,
        description="Tríade clássica: febre + tosse + mialgia + coriza"
    )
    ed.add_rule_programmatic(
        "R18", "Hipótese: COVID-19 suspeito",
        [("febre", "=", "sim"), ("tosse", "=", "sim"), ("falta_ar", "=", "moderada")],
        ("hipotese_diagnostica", "COVID-19 / SRAG — solicitar teste"),
        priority=13,
        description="Síndrome respiratória aguda com febre e tosse"
    )
    ed.add_rule_programmatic(
        "R19", "Hipótese: Amigdalite Bacteriana",
        [("dor_garganta", "=", "sim"), ("febre", "=", "sim"),
         ("amigdalas_exsudato", "=", "sim"), ("coriza", "=", "nao")],
        ("hipotese_diagnostica", "Amigdalite Bacteriana (avaliar antibiótico)"),
        priority=12,
        description="Critérios de Centor: exsudato + febre + sem coriza"
    )
    ed.add_rule_programmatic(
        "R20", "Hipótese: Gastroenterite Aguda",
        [("diarreia", "!=", "nao"), ("náusea_vomito", "=", "sim"),
         ("dor_abdominal", "!=", "nao")],
        ("hipotese_diagnostica", "Gastroenterite Aguda (viral ou bacteriana)"),
        priority=12,
        description="Tríade: diarreia + vômito + dor abdominal"
    )
    ed.add_rule_programmatic(
        "R21", "Hipótese: Dengue Clássica",
        [("febre", "=", "sim"), ("dor_corpo", "=", "sim"),
         ("dor_olhos", "=", "sim"), ("contato_dengue", "=", "sim")],
        ("hipotese_diagnostica", "Dengue — solicitar NS1/sorologia"),
        priority=13,
        description="Febre + mialgia + dor retroocular + epidemiologia"
    )
    ed.add_rule_programmatic(
        "R22", "Hipótese: Dengue com Sinais de Alarme",
        [("manchas_pele", "=", "petequias"), ("sangramento_espontaneo", "=", "sim")],
        ("hipotese_diagnostica", "Dengue Grave — internação urgente"),
        priority=17,
        description="Petéquias + sangramento — dengue grave"
    )
    ed.add_rule_programmatic(
        "R23", "Hipótese: Infecção Urinária Baixa (Cistite)",
        [("disuria", "=", "sim"), ("polaciuria", "=", "sim"),
         ("urina_turva", "=", "sim"), ("febre", "=", "nao")],
        ("hipotese_diagnostica", "Cistite — ITU Baixa"),
        priority=11,
        description="Disúria + polaciúria + urina turva sem febre"
    )
    ed.add_rule_programmatic(
        "R24", "Hipótese: Pielonefrite",
        [("disuria", "=", "sim"), ("febre", "=", "sim"),
         ("dor_lombar_flanco", "=", "sim")],
        ("hipotese_diagnostica", "Pielonefrite — ITU Alta (internação a avaliar)"),
        priority=14,
        description="ITU + febre + dor em flanco — infecção renal"
    )
    ed.add_rule_programmatic(
        "R25", "Hipótese: Crise Hipertensiva",
        [("pressao_sistolica", ">", "180"), ("historico_hipertensao", "=", "sim")],
        ("hipotese_diagnostica", "Crise Hipertensiva — Urgência/Emergência"),
        priority=16,
        description="PAS > 180 em hipertenso conhecido"
    )
    ed.add_rule_programmatic(
        "R26", "Hipótese: Crise Asmática",
        [("chiado_peito", "=", "sim"), ("historico_asma", "=", "sim"),
         ("falta_ar", "=", "moderada")],
        ("hipotese_diagnostica", "Crise Asmática Moderada"),
        priority=14,
        description="Asma + sibilância + dispneia moderada"
    )
    ed.add_rule_programmatic(
        "R27", "Hipótese: Meningite",
        [("febre", "=", "sim"), ("rigidez_nuca", "=", "sim"),
         ("dor_cabeca", "=", "sim")],
        ("hipotese_diagnostica", "Meningite — emergência neurológica"),
        priority=20,
        description="Tríade de Kernig: febre + rigidez + cefaleia"
    )

    # ══════════════════════════════════════════════════════════════════
    # BLOCO 3 — CONDUTA NA TRIAGEM
    # ══════════════════════════════════════════════════════════════════

    ed.add_rule_programmatic(
        "R28", "Conduta: O2 imediato",
        [("saturacao_o2", "<", "94")],
        ("conduta_triagem", "Administrar O₂ imediatamente + acesso venoso + chamar médico"),
        priority=20
    )
    ed.add_rule_programmatic(
        "R29", "Conduta: Antitérmico e hidratação oral",
        [("febre", "=", "sim"), ("desidratação", "=", "nao"),
         ("saturacao_o2", ">=", "95")],
        ("conduta_triagem", "Antitérmico (dipirona/paracetamol) + hidratação oral + repouso"),
        priority=10
    )
    ed.add_rule_programmatic(
        "R30", "Conduta: SRO para diarreia",
        [("diarreia", "!=", "nao"), ("desidratação", "=", "leve")],
        ("conduta_triagem", "Soro de reidratação oral (SRO) + orientação dietética"),
        priority=11
    )
    ed.add_rule_programmatic(
        "R31", "Conduta: SF IV para desidratação moderada",
        [("desidratação", "=", "moderada")],
        ("conduta_triagem", "Hidratação venosa com SF 0,9% + coleta de exames + acesso venoso"),
        priority=14
    )
    ed.add_rule_programmatic(
        "R32", "Conduta: Anti-hipertensivo urgência",
        [("pressao_sistolica", ">", "180"), ("nivel_consciencia", "=", "alerta")],
        ("conduta_triagem", "Captopril 25mg SL ou Nitrendipina + monitorização + ECG"),
        priority=16
    )
    ed.add_rule_programmatic(
        "R33", "Conduta: Nebulização para asma",
        [("chiado_peito", "=", "sim"), ("falta_ar", "!=", "nao")],
        ("conduta_triagem", "Nebulização com salbutamol + corticoide sistêmico + oximetria contínua"),
        priority=14
    )

    # ══════════════════════════════════════════════════════════════════
    # BLOCO 4 — ENCAMINHAMENTO
    # ══════════════════════════════════════════════════════════════════

    ed.add_rule_programmatic(
        "R34", "Encaminhamento: Sala de Emergência",
        [("nivel_consciencia", "!=", "alerta")],
        ("encaminhamento", "SALA DE EMERGÊNCIA — atendimento imediato"),
        priority=20
    )
    ed.add_rule_programmatic(
        "R35", "Encaminhamento: Sala de Emergência — SpO2",
        [("saturacao_o2", "<", "90")],
        ("encaminhamento", "SALA DE EMERGÊNCIA — insuficiência respiratória"),
        priority=20
    )
    ed.add_rule_programmatic(
        "R36", "Encaminhamento: Consultório médico urgente",
        [("febre", "=", "sim"), ("prostração", "=", "sim")],
        ("encaminhamento", "CONSULTÓRIO MÉDICO — prioridade amarela"),
        priority=14
    )
    ed.add_rule_programmatic(
        "R37", "Encaminhamento: Sala de hidratação",
        [("desidratação", "=", "moderada"), ("diarreia", "!=", "nao")],
        ("encaminhamento", "SALA DE HIDRATAÇÃO — reidratação venosa supervisionada"),
        priority=13
    )
    ed.add_rule_programmatic(
        "R38", "Encaminhamento: Consultório verde",
        [("febre", "=", "nao"), ("falta_ar", "=", "nao"),
         ("desidratação", "=", "nao")],
        ("encaminhamento", "CONSULTÓRIO MÉDICO — fila verde (aguardar)"),
        priority=8
    )

    # ══════════════════════════════════════════════════════════════════
    # BLOCO 5 — ORIENTAÇÕES AO PACIENTE
    # ══════════════════════════════════════════════════════════════════

    ed.add_rule_programmatic(
        "R39", "Orientação: Isolamento respiratório",
        [("tosse", "!=", "nao"), ("febre", "=", "sim")],
        ("orientacao_paciente",
         "Use máscara; mantenha distância de outros; informe ao médico sintomas há quantos dias"),
        priority=12
    )
    ed.add_rule_programmatic(
        "R40", "Orientação: Hidratação e dieta",
        [("diarreia", "!=", "nao"), ("náusea_vomito", "=", "sim")],
        ("orientacao_paciente",
         "Ingerir SRO aos poucos; evitar alimentos sólidos até melhora; não tomar antidiarreico sem prescrição"),
        priority=10
    )
    ed.add_rule_programmatic(
        "R41", "Orientação: Retorno imediato",
        [("criança_menor_5", "=", "sim"), ("febre", "=", "sim")],
        ("orientacao_paciente",
         "Criança menor de 5 anos com febre: prioridade. Retornar imediatamente se convulsão, recusa alimentar ou piora"),
        priority=15
    )
    ed.add_rule_programmatic(
        "R42", "Orientação: Idoso com febre",
        [("idoso_maior_60", "=", "sim"), ("febre", "=", "sim")],
        ("orientacao_paciente",
         "Paciente idoso: maior risco de complicações. Acompanhante deve permanecer; monitorar nível de consciência"),
        priority=15
    )

    return kb


if __name__ == "__main__":
    kb = build_triagem_kb()
    out_path = os.path.join(os.path.dirname(__file__), "triagem_upa_kb.json")
    kb.save(out_path)
    print(f"✅ KB gerada: {out_path}")
    print(f"   Regras:    {len(kb.rules)}")
    print(f"   Perguntas: {len(kb.questions)}")
    print(f"   Hipóteses: {kb.hypotheses}")
