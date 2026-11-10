# -*- coding: utf-8 -*-
"""
Simulador do subsistema de E/S (camadas 1 e 2). FORNECIDO — não precisam alterar.

Simulação por eventos discretos:
  1. as requisições da carga chegam nos seus instantes;
  2. com a cache ativa (M1), leituras com todos os blocos na cache terminam na hora e
     escritas em write-back terminam na hora; o resto entra na fila;
  3. quando o disco está livre e há fila, o escalonador escolhe a próxima requisição;
  4. o disco atende uma requisição por vez (sem preempção); o tempo vem do modelo do disco;
  5. o custo de CPU de cada atendimento vem de cpu.custo_cpu(modo, ...).
"""
from simes import parametros as P
from simes.es.cpu import custo_cpu
from simes.es.requisicao import Requisicao
from simes.metricas import media, percentil


def copiar(requisicoes):
    """Cópias novas, para rodar a mesma carga em várias configurações."""
    return [Requisicao(r.id, r.chegada, r.processo, r.tipo, r.bloco, r.n_blocos) for r in requisicoes]


def simular_es(requisicoes, escalonador, disco, modo_cpu="interrupcao", cache=None, queda_ms=None):
    reqs = sorted(copiar(requisicoes), key=lambda r: (r.chegada, r.id))
    n = len(reqs)
    fila = []
    concluidas = []
    faltantes = {}                # id da requisição -> blocos que faltaram na cache
    agora = 0.0
    direcao = +1
    cpu_es = 0.0
    escritas_fisicas = 0
    acertos = faltas = 0
    perdidos = None
    proximo_id = [n]
    proximo_sync = P.INTERVALO_SYNC_MS if (cache is not None and cache.escrita == "write-back") else float("inf")

    def gravacao_interna(bloco, instante):
        r = Requisicao(proximo_id[0], instante, "cache", "E", bloco, 1, origem="cache")
        proximo_id[0] += 1
        fila.append(r)

    def chegar(r):
        nonlocal acertos, faltas
        if cache is None:
            fila.append(r)
            return
        blocos = range(r.bloco, r.bloco + r.n_blocos)
        if r.tipo == "L":
            faltou = [b for b in blocos if not cache.ler(b)]
            if not faltou:
                acertos += 1
                r.inicio = r.chegada
                r.fim = r.chegada + r.n_blocos * P.CUSTO_ACERTO_CACHE_MS
                concluidas.append(r)
            else:
                faltas += 1
                faltantes[r.id] = faltou
                fila.append(r)
        else:
            gravar = []
            for b in blocos:
                gravar.extend(cache.escrever(b))
            if cache.escrita == "write-through":
                fila.append(r)                         # a própria escrita vai ao disco
                for b in gravar:
                    if not (r.bloco <= b < r.bloco + r.n_blocos):
                        gravacao_interna(b, r.chegada)
            else:
                r.inicio = r.chegada
                r.fim = r.chegada + r.n_blocos * P.CUSTO_ACERTO_CACHE_MS
                concluidas.append(r)
                for b in gravar:
                    gravacao_interna(b, r.chegada)

    i = 0
    while i < n or fila:
        if not fila and i < n:
            agora = max(agora, reqs[i].chegada)
        if queda_ms is not None and perdidos is None and agora >= queda_ms:
            perdidos = cache.sujos() if cache is not None else 0
        while cache is not None and agora >= proximo_sync:
            for b in cache.sincronizar():
                gravacao_interna(b, proximo_sync)
            proximo_sync += P.INTERVALO_SYNC_MS
        while i < n and reqs[i].chegada <= agora:
            chegar(reqs[i])
            i += 1
        if not fila:
            continue

        indice, direcao, passar_por = escalonador.escolher(fila, disco.cilindro_atual, direcao,
                                                           agora, disco.cilindros - 1)
        r = fila.pop(indice)
        t = agora
        for c in passar_por:
            duracao, _ = disco.mover(c)
            t += duracao
        duracao, _ = disco.atender(r.bloco, r.n_blocos, r.tipo)
        t += duracao
        r.inicio, r.fim = agora, t
        cpu_es += custo_cpu(modo_cpu, r.n_blocos, t - agora)
        if r.tipo == "E":
            escritas_fisicas += r.n_blocos
        agora = t
        if r.origem == "usuario":
            concluidas.append(r)
            if cache is not None and r.tipo == "L":
                for b in faltantes.pop(r.id, []):
                    for sujo in cache.inserir(b):
                        gravacao_interna(sujo, agora)

    if queda_ms is not None and perdidos is None:
        perdidos = cache.sujos() if cache is not None else 0

    usuarios = [r for r in concluidas if r.origem == "usuario"]
    fim = max((r.fim for r in usuarios), default=0.0)
    respostas = [r.resposta for r in usuarios]
    return {
        "requisicoes": len(usuarios),
        "deslocamento_total": disco.deslocamento_total,
        "tempo_total_ms": fim,
        "resposta_media_ms": media(respostas),
        "resposta_p95_ms": percentil(respostas, 95),
        "espera_max_ms": max((r.espera for r in usuarios), default=0.0),
        "vazao_req_s": len(usuarios) / (fim / 1000.0) if fim > 0 else 0.0,
        "cpu_es_pct": 100.0 * cpu_es / fim if fim > 0 else 0.0,
        "acerto_cache_pct": (100.0 * acertos / (acertos + faltas)) if cache is not None and (acertos + faltas) else None,
        "escritas_fisicas": escritas_fisicas,
        "perdidos_na_queda": perdidos,
        "concluidas": usuarios,
    }
