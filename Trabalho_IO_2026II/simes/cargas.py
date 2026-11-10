# -*- coding: utf-8 -*-
"""
Leitura e geração de cargas de trabalho. FORNECIDO.

Carga de E/S (arquivos cargas/es_*.txt) — uma requisição por linha:
    tempo_ms,processo,tipo,bloco,n_blocos
    0.0,P1,L,120000,8

Carga do sistema de arquivos (arquivos cargas/fs_*.txt) — uma operação por linha:
    tempo_ms processo operacao argumentos...
    0.0 P1 mkdir /src
    1.0 P1 create /src/main.c 24576
    2.0 P1 open /src/main.c r h1
    3.0 P1 read h1 4096
Linhas vazias e linhas começando com # são ignoradas.
"""
import random

from simes import parametros as P
from simes.es.requisicao import Requisicao


# ------------------------------------------------------------------ leitura
def ler_carga_es(caminho):
    requisicoes = []
    with open(caminho, encoding="utf-8") as f:
        for n, linha in enumerate(f, start=1):
            linha = linha.strip()
            if not linha or linha.startswith("#") or linha.startswith("tempo"):
                continue
            partes = [x.strip() for x in linha.split(",")]
            if len(partes) != 5:
                raise ValueError("%s:%d: esperado tempo,processo,tipo,bloco,n_blocos" % (caminho, n))
            t, proc, tipo, bloco, nb = partes
            requisicoes.append(Requisicao(len(requisicoes), float(t), proc, tipo, int(bloco), int(nb)))
    requisicoes.sort(key=lambda r: (r.chegada, r.id))
    return requisicoes


def gravar_carga_es(requisicoes, caminho, comentario=""):
    with open(caminho, "w", encoding="utf-8") as f:
        if comentario:
            for l in comentario.strip().split("\n"):
                f.write("# %s\n" % l)
        f.write("tempo_ms,processo,tipo,bloco,n_blocos\n")
        for r in requisicoes:
            f.write("%.3f,%s,%s,%d,%d\n" % (r.chegada, r.processo, r.tipo, r.bloco, r.n_blocos))


def ler_carga_arquivos(caminho):
    """Devolve uma lista de (tempo_ms, processo, operacao, [argumentos])."""
    operacoes = []
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            partes = linha.split()
            operacoes.append((float(partes[0]), partes[1], partes[2], partes[3:]))
    return operacoes


# ------------------------------------------------------------------ geração
def _chegadas(rng, n, intervalo_medio_ms):
    t = 0.0
    for _ in range(n):
        t += rng.expovariate(1.0 / intervalo_medio_ms)
        yield t


def gerar_es(tipo, n=2000, semente=2026, intervalo_medio_ms=12.0, n_blocos=8, fracao_leitura=0.7):
    """
    Gera uma carga de E/S sintética.
    tipo: 'sequencial' | 'aleatoria' | 'concentrada' | 'rajadas' | 'reuso'
    """
    rng = random.Random(semente)
    limite = P.TOTAL_BLOCOS - max(n_blocos, 1)
    reqs = []

    def nova(t, proc, bloco, nb=n_blocos, tipo_op=None):
        tipo_op = tipo_op or ("L" if rng.random() < fracao_leitura else "E")
        reqs.append(Requisicao(len(reqs), t, proc, tipo_op, bloco, nb))

    if tipo == "sequencial":
        # dois processos varrendo arquivos grandes em regiões distantes do disco
        posicoes = {"P1": 20000, "P2": 250000}
        for i, t in enumerate(_chegadas(rng, n, intervalo_medio_ms / 2.0)):
            proc = "P1" if i % 2 == 0 else "P2"
            nova(t, proc, posicoes[proc], tipo_op="L" if proc == "P1" else "E")
            posicoes[proc] += n_blocos
    elif tipo == "aleatoria":
        for t in _chegadas(rng, n, intervalo_medio_ms):
            nova(t, "P%d" % rng.randint(1, 4), rng.randint(0, limite))
    elif tipo == "concentrada":
        quente = int(P.TOTAL_BLOCOS * 0.2)
        for t in _chegadas(rng, n, intervalo_medio_ms):
            if rng.random() < 0.8:
                bloco = rng.randint(0, quente - n_blocos)
            else:
                bloco = rng.randint(0, limite)
            nova(t, "P%d" % rng.randint(1, 4), bloco)
    elif tipo == "rajadas":
        por_rajada = 50
        for k in range(n // por_rajada):
            t0 = k * 600.0
            for _ in range(por_rajada):
                nova(t0, "P%d" % rng.randint(1, 4), rng.randint(0, limite))
    elif tipo == "reuso":
        # poucos blocos muito acessados e muitos pouco acessados (distribuição de Zipf)
        n_paginas = 4000
        paginas = rng.sample(range(0, limite), n_paginas)
        pesos = [1.0 / (i + 1) for i in range(n_paginas)]
        escolhidas = rng.choices(paginas, weights=pesos, k=n)
        for t, bloco in zip(_chegadas(rng, n, intervalo_medio_ms), escolhidas):
            nova(t, "P%d" % rng.randint(1, 4), bloco, nb=1)
    else:
        raise ValueError("tipo de carga desconhecido: %s" % tipo)
    reqs.sort(key=lambda r: (r.chegada, r.id))
    for i, r in enumerate(reqs):
        r.id = i
    return reqs
