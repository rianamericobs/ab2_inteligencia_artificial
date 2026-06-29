from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

# ==========================================
# 1. MODELAGEM DA REDE (Representação do Conhecimento)
# ==========================================
# Aqui definimos as arestas. As doenças (Dengue, Chikungunya) causam os sintomas.
model = DiscreteBayesianNetwork([
    ('Dengue', 'Febre_Alta'),
    ('Chikungunya', 'Febre_Alta'),
    ('Dengue', 'Dor_Articular'),
    ('Chikungunya', 'Dor_Articular'),
    ('Dengue', 'Manchas_Pele'),
    ('Chikungunya', 'Manchas_Pele')
])

# ==========================================
# 2. TABELAS DE PROBABILIDADES CONDICIONAIS (CPTs)
# ==========================================
# Definindo as probabilidades a priori das doenças (Prevalência base)
cpd_dengue = TabularCPD(
    variable='Dengue', variable_card=2, 
    values=[[0.15], [0.85]], # 15% Sim, 85% Não
    state_names={'Dengue': ['Sim', 'Nao']}
)

cpd_chikungunya = TabularCPD(
    variable='Chikungunya', variable_card=2, 
    values=[[0.05], [0.95]], # 5% Sim, 95% Não
    state_names={'Chikungunya': ['Sim', 'Nao']}
)

# Definindo CPTs para os sintomas
# A ordem das evidências é: ['Dengue', 'Chikungunya']
# As colunas representam as combinações: (Sim, Sim), (Sim, Não), (Não, Sim), (Não, Não)

cpd_febre = TabularCPD(
    variable='Febre_Alta', variable_card=2,
    values=[
        [0.99, 0.90, 0.95, 0.05],  # Probabilidades de Febre_Alta = Sim
        [0.01, 0.10, 0.05, 0.95]   # Probabilidades de Febre_Alta = Não
    ],
    evidence=['Dengue', 'Chikungunya'], evidence_card=[2, 2],
    state_names={'Febre_Alta': ['Sim', 'Nao'], 'Dengue': ['Sim', 'Nao'], 'Chikungunya': ['Sim', 'Nao']}
)

cpd_dor = TabularCPD(
    variable='Dor_Articular', variable_card=2,
    values=[
        [0.95, 0.40, 0.90, 0.10],  # Probabilidades de Dor_Articular = Sim
        [0.05, 0.60, 0.10, 0.90]   # Probabilidades de Dor_Articular = Não
    ],
    evidence=['Dengue', 'Chikungunya'], evidence_card=[2, 2],
    state_names={'Dor_Articular': ['Sim', 'Nao'], 'Dengue': ['Sim', 'Nao'], 'Chikungunya': ['Sim', 'Nao']}
)

cpd_manchas = TabularCPD(
    variable='Manchas_Pele', variable_card=2,
    values=[
        [0.80, 0.50, 0.60, 0.05],  # Probabilidades de Manchas_Pele = Sim
        [0.20, 0.50, 0.40, 0.95]   # Probabilidades de Manchas_Pele = Não
    ],
    evidence=['Dengue', 'Chikungunya'], evidence_card=[2, 2],
    state_names={'Manchas_Pele': ['Sim', 'Nao'], 'Dengue': ['Sim', 'Nao'], 'Chikungunya': ['Sim', 'Nao']}
)

# Adicionando as CPTs ao modelo
model.add_cpds(cpd_dengue, cpd_chikungunya, cpd_febre, cpd_dor, cpd_manchas)

# Validando o modelo (verifica se todas as distribuições somam 1)
assert model.check_model(), "Erro: As tabelas de probabilidade não estão corretas."

# ==========================================
# 3. MOTOR DE INFERÊNCIA E EXPERIMENTOS
# ==========================================
# Inicializando o motor de Eliminação de Variáveis para fazer as predições
infer = VariableElimination(model)

print("="*60)
print("SISTEMA DE DIAGNÓSTICO MÉDICO - REDE BAYESIANA")
print("="*60)

# Experimento 1: Inferência diagnóstica a partir de sintomas básicos
print("\n[EXPERIMENTO 1] Paciente chega com Febre Alta e Dor Articular Intensa.")
print("Evidências: Febre = Sim, Dor Articular = Sim")
res_exp1 = infer.query(variables=['Dengue', 'Chikungunya'], evidence={'Febre_Alta': 'Sim', 'Dor_Articular': 'Sim'})
print(res_exp1)

# Experimento 2: Atualização do diagnóstico após a inclusão de um novo sintoma
print("\n[EXPERIMENTO 2] O mesmo paciente retorna relatando Manchas na Pele.")
print("Evidências: Febre = Sim, Dor Articular = Sim, Manchas = Sim")
res_exp2 = infer.query(variables=['Dengue', 'Chikungunya'], evidence={'Febre_Alta': 'Sim', 'Dor_Articular': 'Sim', 'Manchas_Pele': 'Sim'})
print(res_exp2)

# Experimento 3: Comparação com conjunto de evidências diferente
print("\n[EXPERIMENTO 3] Novo paciente chega com Febre e Manchas, mas sem dor nas juntas.")
print("Evidências: Febre = Sim, Dor Articular = Nao, Manchas = Sim")
res_exp3 = infer.query(variables=['Dengue', 'Chikungunya'], evidence={'Febre_Alta': 'Sim', 'Dor_Articular': 'Nao', 'Manchas_Pele': 'Sim'})
print(res_exp3)
