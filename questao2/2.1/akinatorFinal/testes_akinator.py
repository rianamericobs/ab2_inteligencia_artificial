#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mini_akinator import carregarBase, candidatosCompativeis, escolherMelhorPergunta, ranking


def simularParaEntidade(alvo, base):
    atributos = base["atributos"]
    entidades = base["entidades"]
    respostas = {}
    atributosPerguntados = set()
    totalPerguntas = 0

    while True:
        candidatos = candidatosCompativeis(entidades, respostas)
        if len(candidatos) <= 1:
            break
        if len(atributosPerguntados) >= len(atributos):
            break
        atributo = escolherMelhorPergunta(atributos, candidatos, atributosPerguntados)
        if atributo is None:
            break
        respostas[atributo] = alvo["atributos"][atributo]
        atributosPerguntados.add(atributo)
        totalPerguntas += 1

    entidadeEscolhida = ranking(entidades, respostas)[0]
    acertou = entidadeEscolhida["nome"] == alvo["nome"]
    return totalPerguntas, entidadeEscolhida["nome"], acertou


def main():
    base = carregarBase()
    resultados = []
    for entidade in base["entidades"]:
        totalPerguntas, entidadeEscolhida, acertou = simularParaEntidade(entidade, base)
        resultados.append((entidade["nome"], totalPerguntas, entidadeEscolhida, acertou))

    mediaPerguntas = sum(resultado[1] for resultado in resultados) / len(resultados)
    taxaAcerto = sum(1 for resultado in resultados if resultado[3]) / len(resultados) * 100

    print("Resultados simulados do Mini Akinator")
    print("-" * 50)
    for alvo, totalPerguntas, entidadeEscolhida, acertou in resultados:
        status = "OK" if acertou else "FALHA"
        print(f"Alvo: {alvo:24s} | Perguntas: {totalPerguntas:2d} | Resposta: {entidadeEscolhida:24s} | {status}")

    print("-" * 50)
    print(f"Número médio de perguntas: {mediaPerguntas:.2f}")
    print(f"Taxa de acerto simulada: {taxaAcerto:.1f}%")


if __name__ == "__main__":
    main()
