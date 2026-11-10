# -*- coding: utf-8 -*-
"""
Definição e execução dos experimentos X1–X13. FORNECIDO — não alterem as configurações.

Cada experimento roda o simulador em várias configurações e grava os indicadores em
resultados/*.csv. Experimentos de módulos ainda não implementados aparecem como
"nao_implementado" em resultados/experimentos.csv (isso é esperado para os módulos que o
grupo não escolheu).

Uso:  python executar.py experimentos            (todos)
      python executar.py experimentos X1 X4      (só alguns)
"""
import os
import time
import traceback
from collections import OrderedDict

from simes import parametros as P
from simes.cargas import gerar_es, ler_carga_arquivos, ler_carga_es
from simes.cargas_arquivos import fs_profundidade
from simes.disco import DiscoHDD, criar_disco
from simes.es.buffering import simular_buffering
from simes.es.cache import criar_cache
from simes.es.escalonadores import criar_escalonador
from simes.es.simulador import simular_es
from simes.arquivos.simulador import montar_sistema, simular_arquivos
from simes.metricas import GravadorCSV, formatar_extras

AQUI = os.path.dirname(os.path.abspath(__file__))
CARGAS = os.path.join(AQUI, "cargas")


def carga_es(nome):
    return ler_carga_es(os.path.join(CARGAS, "es_%s.txt" % nome))


def carga_fs(nome):
    return ler_carga_arquivos(os.path.join(CARGAS, "fs_%s.txt" % nome))


def linha_es(exp, carga, esc, disp, modo, res, cache="nenhuma", capacidade="", escrita="",
             n_blocos="", intervalo="", extras=None):
    return {
        "experimento": exp, "carga": carga, "escalonador": esc, "dispositivo": disp,
        "modo_cpu": modo, "cache": cache, "capacidade_cache": capacidade, "escrita": escrita,
        "n_blocos_req": n_blocos, "intervalo_medio_ms": intervalo,
        "requisicoes": res["requisicoes"], "deslocamento_total": res["deslocamento_total"],
        "tempo_total_ms": res["tempo_total_ms"], "resposta_media_ms": res["resposta_media_ms"],
        "resposta_p95_ms": res["resposta_p95_ms"], "espera_max_ms": res["espera_max_ms"],
        "vazao_req_s": res["vazao_req_s"], "cpu_es_pct": res["cpu_es_pct"],
        "acerto_cache_pct": res["acerto_cache_pct"], "escritas_fisicas": res["escritas_fisicas"],
        "perdidos_na_queda": res["perdidos_na_queda"], "extras": formatar_extras(extras or {}),
    }


def registrar_fs(g, exp, carga, alocador, bloqueio, res):
    linha = {k: res[k] for k in ("operacoes", "erros", "acessos_total", "acessos_por_op",
                                 "tempo_total_ms", "tempo_medio_op_ms", "max_tabela_global",
                                 "max_tabela_processo", "max_soma_tabelas_processo",
                                 "max_contador_aberturas")}
    linha.update({"experimento": exp, "carga": carga, "alocador": alocador, "bloqueio": bloqueio,
                  "extras": formatar_extras(res["extras"])})
    g.adicionar("arquivos.csv", linha)
    for op, r in res["por_operacao"].items():
        g.adicionar("arquivos_por_operacao.csv", {
            "experimento": exp, "carga": carga, "alocador": alocador, "bloqueio": bloqueio,
            "operacao": op, "n": r["n"], "erros": r["erros"],
            "acessos_medios": r["acessos_medios"], "tempo_medio_ms": r["tempo_medio_ms"]})


def rodar_fs(g, exp, carga, operacoes, alocador="contigua", bloqueio="consultivo", total_blocos=P.TOTAL_BLOCOS):
    sistema = montar_sistema(alocador, total_blocos=total_blocos, bloqueio=bloqueio)
    res = simular_arquivos(operacoes, sistema)
    registrar_fs(g, exp, carga, alocador, bloqueio, res)
    return 1


# ================================================================== núcleo
def x1(g):
    """Escalonadores (FCFS, SSTF, SCAN) sob quatro padrões de carga."""
    n = 0
    for carga in ("sequencial", "aleatoria", "concentrada", "rajadas"):
        reqs = carga_es(carga)
        for esc in ("FCFS", "SSTF", "SCAN"):
            res = simular_es(reqs, criar_escalonador(esc), DiscoHDD(), "interrupcao")
            g.adicionar("es.csv", linha_es("X1", carga, esc, "hdd", "interrupcao", res))
            n += 1
    return n


def x2(g):
    """Polling × interrupção em um disco rígido e em um dispositivo rápido."""
    n = 0
    for disp in ("hdd", "rapido"):
        for carga in ("aleatoria", "sequencial"):
            reqs = carga_es(carga)
            for modo in ("polling", "interrupcao"):
                res = simular_es(reqs, criar_escalonador("FCFS"), criar_disco(disp), modo)
                g.adicionar("es.csv", linha_es("X2", carga, "FCFS", disp, modo, res))
                n += 1
    return n


def x3(g):
    """Acesso sequencial (compilador) × acesso direto (banco de dados)."""
    return rodar_fs(g, "X3", "compilador", carga_fs("compilador")) + \
        rodar_fs(g, "X3", "banco_dados", carga_fs("banco_dados"))


def x4(g):
    """Custo de resolver caminhos conforme a profundidade (1 a 10 diretórios)."""
    n = 0
    for d in range(1, 11):
        ops = [(float(l.split()[0]), l.split()[1], l.split()[2], l.split()[3:]) for l in fs_profundidade(d)]
        n += rodar_fs(g, "X4", "profundidade_%02d" % d, ops)
    return n


def x5(g):
    """Tabelas de arquivos abertos com vários processos (servidor web)."""
    return rodar_fs(g, "X5", "servidor_web", carga_fs("servidor_web"))


# ================================================================== módulos
def x6(g):
    """M1: cache LRU × FIFO, capacidade, write-through × write-back, queda de energia."""
    reqs = carga_es("reuso")
    queda = reqs[len(reqs) // 2].chegada
    res = simular_es(reqs, criar_escalonador("FCFS"), DiscoHDD(), "interrupcao", queda_ms=queda)
    g.adicionar("es.csv", linha_es("X6", "reuso", "FCFS", "hdd", "interrupcao", res, extras={"queda_ms": queda}))
    n = 1
    for nome in ("LRU", "FIFO"):
        for cap in (64, 128, 256, 512, 1024, 2048):
            for escrita in ("write-through", "write-back"):
                cache = criar_cache(nome, cap, escrita)
                res = simular_es(reqs, criar_escalonador("FCFS"), DiscoHDD(), "interrupcao", cache=cache, queda_ms=queda)
                g.adicionar("es.csv", linha_es("X6", "reuso", "FCFS", "hdd", "interrupcao", res, cache=nome,
                                               capacidade=cap, escrita=escrita, extras={"queda_ms": queda}))
                n += 1
    return n


def x7(g):
    """M2: escalonadores avançados sob carga crescente e concentrada (inanição e justiça)."""
    n = 0
    for intervalo in (14.0, 11.0, 9.0, 8.0):
        reqs = gerar_es("concentrada", n=2000, semente=7, intervalo_medio_ms=intervalo)
        for esc in ("FCFS", "SSTF", "SCAN", "C-SCAN", "LOOK", "C-LOOK", "DEADLINE"):
            res = simular_es(reqs, criar_escalonador(esc), DiscoHDD(), "interrupcao")
            g.adicionar("es.csv", linha_es("X7", "concentrada_crescente", esc, "hdd", "interrupcao", res,
                                           intervalo=intervalo))
            n += 1
    return n


def x8(g):
    """M3: interrupção × DMA conforme o tamanho da requisição; buffering simples × duplo × circular."""
    n = 0
    for nb in (1, 8, 64, 256):
        reqs = gerar_es("aleatoria", n=1000, semente=11, intervalo_medio_ms=40.0, n_blocos=nb)
        for modo in ("polling", "interrupcao", "dma"):
            res = simular_es(reqs, criar_escalonador("FCFS"), DiscoHDD(), modo)
            g.adicionar("es.csv", linha_es("X8", "aleatoria", "FCFS", "hdd", modo, res, n_blocos=nb, intervalo=40.0))
            n += 1
    for consumo in (0.5, 2.0, 8.0):
        for nbuf in (1, 2, 3):
            r = simular_buffering(nbuf, 2.0, consumo, 500)
            g.adicionar("buffering.csv", {"experimento": "X8", "n_buffers": nbuf, "producao_ms": 2.0,
                                          "consumo_ms": consumo, "blocos": 500, **r})
            n += 1
    return n


def x9(g):
    """M4: hard links, links simbólicos, ponteiros pendentes e ciclos."""
    return rodar_fs(g, "X9", "links", carga_fs("links"))


def x10(g):
    """M5: proteção (rwx × ACL) e travas consultivas × mandatórias."""
    ops = carga_fs("protecao")
    return rodar_fs(g, "X10", "protecao", ops, bloqueio="consultivo") + \
        rodar_fs(g, "X10", "protecao", ops, bloqueio="mandatorio")


def x11(g):
    """M6: alocação contígua × encadeada × FAT × indexada numa partição de 20.000 blocos."""
    ops = carga_fs("alocacao")
    n = 0
    for aloc in ("contigua", "encadeada", "fat", "indexada"):
        n += rodar_fs(g, "X11", "alocacao", ops, alocador=aloc, total_blocos=20000)
    return n


def x12(g):
    """Integração: cargas de arquivos -> requisições de E/S -> cache e escalonador."""
    from simes.integracao import historico_para_requisicoes
    n = 0
    alocadores = ["contigua"]
    try:
        montar_sistema("indexada", total_blocos=1000)      # só para saber se o M6 existe
        alocadores.append("indexada")
    except NotImplementedError:
        pass
    usar_cache = True
    try:
        criar_cache("LRU", 1024, "write-back")
    except NotImplementedError:
        usar_cache = False
    for carga in ("compilador", "banco_dados"):
        ops = carga_fs(carga)
        for aloc in alocadores:
            sistema = montar_sistema(aloc, guardar_historico=True)
            simular_arquivos(ops, sistema)
            reqs = historico_para_requisicoes(sistema.camada.historico)
            for esc in ("FCFS", "SSTF", "SCAN"):
                for com_cache in ([False, True] if usar_cache else [False]):
                    cache = criar_cache("LRU", 1024, "write-back") if com_cache else None
                    res = simular_es(reqs, criar_escalonador(esc), DiscoHDD(), "interrupcao", cache=cache)
                    g.adicionar("es.csv", linha_es("X12", "%s+%s" % (carga, aloc), esc, "hdd", "interrupcao", res,
                                                   cache="LRU" if com_cache else "nenhuma",
                                                   capacidade=1024 if com_cache else "",
                                                   escrita="write-back" if com_cache else ""))
                    n += 1
    return n


def x13(g):
    """Bônus: armazenamento flash × disco rígido."""
    n = 0
    for carga in ("reuso", "aleatoria"):
        reqs = carga_es(carga)
        for disp in ("hdd", "flash"):
            disco = criar_disco(disp)
            res = simular_es(reqs, criar_escalonador("FCFS"), disco, "interrupcao")
            extras = {}
            if disp == "flash":
                extras = {"paginas_gravadas_host": disco.paginas_gravadas_host,
                          "paginas_programadas": disco.paginas_programadas,
                          "apagamentos": disco.apagamentos,
                          "amplificacao_escrita": disco.paginas_programadas / float(max(1, disco.paginas_gravadas_host))}
            g.adicionar("es.csv", linha_es("X13", carga, "FCFS", disp, "interrupcao", res, extras=extras))
            n += 1
    return n


EXPERIMENTOS = OrderedDict([
    ("X1", ("núcleo", x1)), ("X2", ("núcleo", x2)), ("X3", ("núcleo", x3)),
    ("X4", ("núcleo", x4)), ("X5", ("núcleo", x5)),
    ("X6", ("M1", x6)), ("X7", ("M2", x7)), ("X8", ("M3", x8)), ("X9", ("M4", x9)),
    ("X10", ("M5", x10)), ("X11", ("M6", x11)), ("X12", ("integração", x12)), ("X13", ("bônus", x13)),
])


def executar(lista=None, pasta=os.path.join(AQUI, "resultados")):
    final = GravadorCSV(pasta)
    for exp, (parte, funcao) in EXPERIMENTOS.items():
        if lista and exp not in lista:
            continue
        parcial = GravadorCSV(pasta)
        t0 = time.time()
        try:
            n = funcao(parcial)
        except NotImplementedError as e:
            final.adicionar("experimentos.csv", {"experimento": exp, "status": "nao_implementado",
                                                 "execucoes": 0, "detalhe": str(e)})
            print("%-4s %-11s não implementado: %s" % (exp, parte, e))
            continue
        except Exception as e:
            final.adicionar("experimentos.csv", {"experimento": exp, "status": "erro", "execucoes": 0,
                                                 "detalhe": "%s: %s" % (type(e).__name__, e)})
            print("%-4s %-11s ERRO" % (exp, parte))
            traceback.print_exc()
            continue
        for arquivo, linhas in parcial.linhas.items():
            final.linhas[arquivo].extend(linhas)
        final.adicionar("experimentos.csv", {"experimento": exp, "status": "ok", "execucoes": n, "detalhe": ""})
        print("%-4s %-11s ok (%d execuções, %.1f s)" % (exp, parte, n, time.time() - t0))
    final.gravar()
    print("\nResultados gravados em %s" % pasta)
