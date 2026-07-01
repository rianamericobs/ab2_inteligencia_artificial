#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path

caminhoBase = Path(__file__).parent / "dados" / "personagens.json"
respostasSim = {"s", "sim", "y", "yes"}
respostasNao = {"n", "nao", "não", "no"}
respostasNaoSei = {"?", "ns", "nsei", "nao sei", "não sei", "talvez", "t"}


def carregarBase(caminho=caminhoBase):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def normalizarResposta(texto):
    resposta = texto.strip().lower()
    if resposta in respostasSim:
        return True
    if resposta in respostasNao:
        return False
    if resposta in respostasNaoSei:
        return None
    return "invalida"


def candidatosCompativeis(entidades, respostas):
    compativeis = []
    for entidade in entidades:
        atributosEntidade = entidade["atributos"]
        entidadeCompativel = True
        for atributo, resposta in respostas.items():
            if resposta is None:
                continue
            if atributosEntidade.get(atributo) != resposta:
                entidadeCompativel = False
                break
        if entidadeCompativel:
            compativeis.append(entidade)
    return compativeis


def ranking(entidades, respostas):
    pontuacao = []
    for entidade in entidades:
        pontos = 0
        conflitos = 0
        atributosEntidade = entidade["atributos"]
        for atributo, resposta in respostas.items():
            if resposta is None:
                continue
            if atributosEntidade.get(atributo) == resposta:
                pontos += 1
            else:
                conflitos += 1
        pontuacao.append((pontos, -conflitos, entidade))
    pontuacao.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [entidade for _, _, entidade in pontuacao]


def escolherMelhorPergunta(atributos, candidatos, atributosPerguntados):
    melhorAtributo = None
    melhorScore = -1

    for atributo in atributos:
        if atributo in atributosPerguntados:
            continue

        qtdSim = sum(1 for entidade in candidatos if entidade["atributos"].get(atributo) is True)
        qtdNao = sum(1 for entidade in candidatos if entidade["atributos"].get(atributo) is False)

        if qtdSim == 0 or qtdNao == 0:
            continue

        score = min(qtdSim, qtdNao)
        if score > melhorScore:
            melhorScore = score
            melhorAtributo = atributo

    return melhorAtributo


def mostrarHipotese(entidades, respostas):
    entidadesOrdenadas = ranking(entidades, respostas)
    if not entidadesOrdenadas:
        return
    melhorEntidade = entidadesOrdenadas[0]
    print(f"\nHipótese atual mais provável: {melhorEntidade['nome']}")
    print(f"Descrição: {melhorEntidade['descricao']}")


def explicar(entidade, respostas, perguntas):
    print("\nExplicação da conclusão:")
    print(f"O sistema escolheu: {entidade['nome']}.")
    fatosUsados = []
    for atributo, resposta in respostas.items():
        if resposta is None:
            continue
        valorEntidade = entidade["atributos"].get(atributo)
        if valorEntidade == resposta:
            respostaTexto = "sim" if resposta else "não"
            fatosUsados.append(f"- {perguntas[atributo]} Resposta compatível: {respostaTexto}.")

    if fatosUsados:
        print("Fatos compatíveis usados no raciocínio:")
        for fato in fatosUsados:
            print(fato)
    else:
        print("Não houve fatos suficientes; a resposta foi baseada na maior similaridade disponível.")


def jogar():
    base = carregarBase()
    atributos = base["atributos"]
    entidades = base["entidades"]
    respostas = {}
    atributosPerguntados = set()

    print("=" * 60)
    print("MINI AKINATOR")
    print("Responda com: sim, nao ou nao sei")
    print("=" * 60)

    while True:
        candidatos = candidatosCompativeis(entidades, respostas)

        if len(candidatos) == 1:
            entidadeEscolhida = candidatos[0]
            print(f"\nAcho que é: {entidadeEscolhida['nome']}!")
            print(entidadeEscolhida["descricao"])
            explicar(entidadeEscolhida, respostas, atributos)
            break

        if len(atributosPerguntados) >= len(atributos):
            entidadesOrdenadas = ranking(entidades, respostas)
            entidadeEscolhida = entidadesOrdenadas[0]
            print(f"\nNão consegui ter certeza absoluta, mas minha melhor hipótese é: {entidadeEscolhida['nome']}.")
            print(entidadeEscolhida["descricao"])
            explicar(entidadeEscolhida, respostas, atributos)
            print("\nOutras hipóteses possíveis:")
            for entidade in entidadesOrdenadas[1:5]:
                print(f"- {entidade['nome']}")
            break

        if not candidatos:
            print("\nNenhuma entidade ficou totalmente compatível com as respostas.")
            entidadesOrdenadas = ranking(entidades, respostas)
            entidadeEscolhida = entidadesOrdenadas[0]
            print(f"Melhor hipótese por similaridade: {entidadeEscolhida['nome']}")
            explicar(entidadeEscolhida, respostas, atributos)
            break

        mostrarHipotese(candidatos, respostas)
        atributo = escolherMelhorPergunta(atributos, candidatos, atributosPerguntados)

        if atributo is None:
            entidadesOrdenadas = ranking(candidatos, respostas)
            entidadeEscolhida = entidadesOrdenadas[0]
            print(f"\nCom as informações disponíveis, minha resposta é: {entidadeEscolhida['nome']}.")
            print(entidadeEscolhida["descricao"])
            explicar(entidadeEscolhida, respostas, atributos)
            break

        while True:
            entradaUsuario = input(f"\nPergunta: {atributos[atributo]} ").strip()
            resposta = normalizarResposta(entradaUsuario)
            if resposta != "invalida":
                break
            print("Resposta inválida. Use: sim, nao ou nao sei.")

        respostas[atributo] = resposta
        atributosPerguntados.add(atributo)

    print("\nFim da consulta.")


if __name__ == "__main__":
    jogar()
