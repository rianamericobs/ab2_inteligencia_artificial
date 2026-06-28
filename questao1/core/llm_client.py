"""
Módulo: Cliente LLM para Integração com a API do Groq
Fornece inteligência artificial ao Sistema Baseado em Conhecimento.
"""
from __future__ import annotations
import os
import sys
import subprocess
import json
import importlib.util
from typing import Optional, Any

if importlib.util.find_spec("groq") is None:
    try:
        print("\n[Instalação] Dependência 'groq' não encontrada. Instalando automaticamente...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "groq", "-q"])
    except Exception as e:
        print(f"[Aviso] Falha ao instalar a biblioteca 'groq' automaticamente: {e}")

GROQ_AVAILABLE = False
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    pass


def load_dotenv():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    os.environ[k] = v


class GroqClient:
    def __init__(self):
        self.client = None
        self.model = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
        
        if not GROQ_AVAILABLE:
            return

        load_dotenv()
        api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("API_KEY")
        if api_key:
            try:
                self.client = Groq(api_key=api_key)
            except Exception as e:
                print(f"[Erro] Falha ao inicializar o cliente Groq: {e}")
                self.client = None

    def is_available(self) -> bool:
        """Retorna True se o cliente Groq foi configurado e inicializado com sucesso."""
        return self.client is not None

    def map_answer_to_options(self, question: str, options: list[str], user_answer: str) -> Optional[str]:
        """
        Interpreta a resposta livre em linguagem natural do usuário e a mapeia para uma das opções válidas.
        Se não corresponder a nenhuma opção, retorna None ou 'invalido'.
        """
        if not self.is_available():
            return None

        prompt = f"""Dada a pergunta "{question}" e a lista de opções válidas: {options}.
O usuário respondeu: "{user_answer}".

Sua tarefa é analisar a resposta do usuário e determinar se ela corresponde a uma das opções válidas.
Se a resposta corresponder clara ou implicitamente a uma das opções (por exemplo, "Acho que sim" para "sim", "De jeito nenhum" para "não", ou variações de grafia/caso/sinônimos), retorne APENAS a opção exata da lista.
Se a resposta do usuário for uma negação ou confirmação genérica e as opções forem sim/não (ou similares), faça o mapeamento correto.
Se a resposta for ambígua ou não puder ser mapeada de forma alguma para as opções disponíveis, retorne a palavra "invalido".

Não adicione explicações, justificativas ou formatações extras. Responda apenas com a opção exata ou "invalido"."""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Você é um classificador preciso de respostas. Responda APENAS com a opção exata da lista fornecida ou 'invalido' sem formatações adicionais."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.0
            )
            result = chat_completion.choices[0].message.content.strip()
            # Remover aspas ou pontos extras
            result = result.strip('"').strip("'").strip(".")
            if result in options:
                return result
            # Verificar se foi retornado uma correspondência case-insensitive
            for opt in options:
                if opt.lower() == result.lower():
                    return opt
            return None
        except Exception as e:
            # Silencioso, falha para o modo padrão
            return None

    def explain_natural_language(self, structured_explanation: str) -> str:
        """
        Gera uma explicação amigável e em linguagem natural em português a partir da explicação estruturada.
        """
        if not self.is_available():
            return structured_explanation

        prompt = f"""Você é o assistente explicativo do sistema especialista K-RuleShell.
Abaixo está a explicação lógica e estruturada gerada pelo motor de inferência sobre como/por que uma conclusão foi tomada ou uma pergunta foi feita:

{structured_explanation}

Reescreva essa explicação em português de forma natural, amigável, clara e concisa. Explique o raciocínio de maneira fluida e lógica para o usuário final, sem perder a precisão das regras aplicadas."""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Você é um assistente especialista que traduz inferências lógicas complexas em explicações simples e naturais em português."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.3
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            return structured_explanation

    def parse_rule_from_natural_language(self, text: str, current_kb_info: str) -> Optional[dict]:
        """
        Converte uma regra descrita em linguagem natural para um dicionário JSON estruturado compatível com uma Rule.
        """
        if not self.is_available():
            return None

        prompt = f"""Você é um engenheiro de conhecimento especialista em sistemas baseados em regras de produção.
Dada a descrição de uma regra em linguagem natural:
"{text}"

E o contexto da Base de Conhecimento atual (domínio, atributos conhecidos, regras existentes):
"{current_kb_info}"

Gere uma estrutura JSON válida que represente exatamente essa regra. 

O formato de retorno DEVE ser estritamente o seguinte JSON:
{{
  "id": "R...",  // ex: R5 (gere um ID único coerente ou R<num> de acordo com as regras existentes)
  "name": "Nome curto da regra",
  "description": "Descrição detalhada da regra",
  "priority": 0, // prioridade inteira (opcional, padrão 0)
  "conditions": [
    {{
      "attribute": "nome_do_atributo",
      "operator": "=", // ou "!=", ">", "<", ">=", "<="
      "value": "valor"
    }}
  ],
  "conclusion": {{
    "attribute": "nome_do_atributo",
    "value": "valor"
  }}
}}

Instruções importantes:
1. Mapeie os atributos e valores de forma consistente com a base atual se eles já existirem (ex: se o atributo 'febre' existe, use 'febre' em vez de 'temperatura_alta' se o sentido for o mesmo).
2. Atributos devem usar letras minúsculas em snake_case (ex: 'dor_de_cabeca').
3. Operadores válidos: '=', '!=', '>', '<', '>=', '<='.
4. Retorne APENAS o JSON válido. Não coloque blocos de código com ```json ou textos adicionais antes ou depois."""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Você é um parser preciso que converte regras de linguagem natural em objetos JSON estruturados. Retorne apenas JSON puro, sem marcações ou explicações."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.1
            )
            content = chat_completion.choices[0].message.content.strip()
            # Remover marcações markdown se o modelo desobedecer as instruções de sistema
            if content.startswith("```"):
                lines = content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = "\n".join(lines).strip()
            
            return json.loads(content)
        except Exception as e:
            print(f"[Erro] Falha ao parsear regra com a IA: {e}")
            return None

    def parse_rules_from_natural_language(self, text: str, current_kb_info: str) -> Optional[list[dict]]:
        """
        Converte uma ou mais regras descritas em linguagem natural para uma lista de dicionários JSON compatíveis com Rule.
        """
        if not self.is_available():
            return None

        prompt = f"""Você é um engenheiro de conhecimento especialista em sistemas baseados em regras de produção.
Dada a descrição de uma ou mais regras em linguagem natural:
"{text}"

E o contexto da Base de Conhecimento atual (domínio, atributos conhecidos, regras existentes):
"{current_kb_info}"

Gere uma lista JSON válida contendo essas regras estruturadas.

O formato de retorno DEVE ser estritamente uma lista JSON no seguinte formato:
[
  {{
    "id": "R...",  // ex: R5 (gere um ID único coerente ou R<num> de acordo com as regras existentes)
    "name": "Nome curto da regra",
    "description": "Descrição detalhada da regra",
    "priority": 0, // prioridade inteira (opcional, padrão 0)
    "conditions": [
      {{
        "attribute": "nome_do_atributo",
        "operator": "=", // ou "!=", ">", "<", ">=", "<="
        "value": "valor"
      }}
    ],
    "conclusion": {{
      "attribute": "nome_do_atributo",
      "value": "valor"
    }}
  }}
]

Instruções importantes:
1. Mapeie os atributos e valores de forma consistente com a base atual se eles já existirem (ex: se o atributo 'febre' existe, use 'febre' em vez de 'temperatura_alta' se o sentido for o mesmo).
2. Atributos devem usar letras minúsculas em snake_case (ex: 'dor_de_cabeca').
3. Operadores válidos: '=', '!=', '>', '<', '>=', '<='.
4. Retorne APENAS o JSON válido (uma lista JSON). Não coloque blocos de código com ```json ou textos adicionais antes ou depois."""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Você é um parser preciso que converte descrições de regras em uma lista de objetos JSON. Retorne apenas a lista JSON pura, sem marcações ou explicações."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.1
            )
            content = chat_completion.choices[0].message.content.strip()
            if content.startswith("```"):
                lines = content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = "\n".join(lines).strip()
            
            data = json.loads(content)
            if isinstance(data, dict):
                return [data]
            return data
        except Exception as e:
            print(f"[Erro] Falha ao parsear regras com a IA: {e}")
            return None

    def parse_questions_from_natural_language(self, text: str, current_kb_info: str) -> Optional[list[dict]]:
        """
        Converte uma ou mais perguntas descritas em linguagem natural para uma lista de dicionários contendo metadados de perguntas e limites.
        """
        if not self.is_available():
            return None

        prompt = f"""Você é um engenheiro de conhecimento especialista em sistemas baseados em regras de produção.
Dada a descrição de uma ou mais perguntas em linguagem natural:
"{text}"

E o contexto da Base de Conhecimento atual:
"{current_kb_info}"

Gere uma lista JSON contendo as perguntas estruturadas com seus atributos, opções e limites.

O formato de retorno DEVE ser estritamente uma lista JSON no seguinte formato:
[
  {{
    "attribute": "nome_do_atributo",
    "question": "Texto da pergunta ao usuário?",
    "options": ["opcao1", "opcao2"], // opcional (lista de strings ou nulo/vazio se livre)
    "range": [min_val, max_val]      // opcional (se for numérico livre, ex: [0.0, 100.0] ou nulo se não houver limites)
  }}
]

Instruções importantes:
1. Se a pergunta for de sim/nao, preencha as opções como ["sim", "nao"].
2. Se a pergunta for sobre um sinal vital ou campo numérico contínuo, as opções devem ser nulas (vazio), mas tente definir o "range" apropriado (ex: temperatura corporal de 30 a 45, saturação de 0 a 100, idade de 0 a 120, etc).
3. Atributos devem ser snake_case e minúsculos.
4. Retorne APENAS o JSON válido. Não coloque blocos de código com ```json ou explicações."""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Você é um parser preciso que converte descrições de perguntas em uma lista de objetos JSON contendo atributos, perguntas, opções e limites. Retorne apenas JSON puro."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.1
            )
            content = chat_completion.choices[0].message.content.strip()
            if content.startswith("```"):
                lines = content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = "\n".join(lines).strip()
            
            data = json.loads(content)
            if isinstance(data, dict):
                return [data]
            return data
        except Exception as e:
            print(f"[Erro] Falha ao parsear perguntas com a IA: {e}")
            return None
