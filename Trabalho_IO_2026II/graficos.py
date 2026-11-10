# -*- coding: utf-8 -*-
"""
Gera os gráficos padrão a partir de resultados/*.csv, na pasta graficos/. FORNECIDO.

Uso:  python graficos.py

Precisa do matplotlib (pip install --user matplotlib). Sem ele, o script avisa e termina:
nesse caso, façam os gráficos em uma planilha a partir dos CSVs. Podem acrescentar
gráficos próprios, mas mantenham os gerados aqui.
"""
import csv
import os
import sys
from collections import OrderedDict

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "resultados")
SAIDA = os.path.join(AQUI, "graficos")


def ler(nome):
    caminho = os.path.join(RES, nome)
    if not os.path.exists(caminho):
        return []
    with open(caminho, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def extra(linha, chave):
    for par in (linha.get("extras") or "").split(";"):
        if "=" in par:
            k, v = par.split("=", 1)
            if k == chave:
                return num(v)
    return 0.0


def barras(plt, nome, titulo, grupos, series, valores, rotulo_y, log=False):
    """valores[(grupo, serie)] -> número. Gráfico de barras agrupadas."""
    fig, ax = plt.subplots(figsize=(8, 4.2))
    largura = 0.8 / max(1, len(series))
    for k, s in enumerate(series):
        xs = [i + k * largura for i in range(len(grupos))]
        ax.bar(xs, [valores.get((g, s), 0.0) for g in grupos], largura, label=str(s))
    ax.set_xticks([i + largura * (len(series) - 1) / 2.0 for i in range(len(grupos))])
    ax.set_xticklabels([str(g) for g in grupos])
    ax.set_title(titulo)
    ax.set_ylabel(rotulo_y + (" — escala log" if log else ""))
    if log:
        ax.set_yscale("log")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, nome), dpi=130)
    plt.close(fig)


def linhas(plt, nome, titulo, series_xy, rotulo_x, rotulo_y, log=False):
    fig, ax = plt.subplots(figsize=(8, 4.2))
    for s, pontos in series_xy.items():
        pontos = sorted(pontos)
        ax.plot([p[0] for p in pontos], [p[1] for p in pontos], marker="o", label=str(s))
    ax.set_title(titulo)
    ax.set_xlabel(rotulo_x)
    ax.set_ylabel(rotulo_y)
    if log:
        ax.set_yscale("log")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, nome), dpi=130)
    plt.close(fig)


def main():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib não está instalado. Instale com:  pip install --user matplotlib")
        print("ou façam os gráficos numa planilha a partir de resultados/*.csv.")
        sys.exit(1)
    os.makedirs(SAIDA, exist_ok=True)
    es, fs, po, bf = ler("es.csv"), ler("arquivos.csv"), ler("arquivos_por_operacao.csv"), ler("buffering.csv")
    feitos = []

    x1 = [r for r in es if r["experimento"] == "X1"]
    if x1:
        cargas = list(OrderedDict.fromkeys(r["carga"] for r in x1))
        escs = list(OrderedDict.fromkeys(r["escalonador"] for r in x1))
        for met, rot in (("resposta_media_ms", "tempo de resposta médio (ms)"),
                         ("espera_max_ms", "maior espera (ms)"),
                         ("deslocamento_total", "deslocamento total (cilindros)")):
            barras(plt, "X1_%s.png" % met, "X1 — %s" % rot, cargas, escs,
                   {(r["carga"], r["escalonador"]): num(r[met]) for r in x1}, rot, log=True)
        feitos.append("X1")

    x2 = [r for r in es if r["experimento"] == "X2"]
    if x2:
        grupos = list(OrderedDict.fromkeys("%s/%s" % (r["dispositivo"], r["carga"]) for r in x2))
        barras(plt, "X2_cpu.png", "X2 — CPU gasta com E/S", grupos, ["polling", "interrupcao"],
               {("%s/%s" % (r["dispositivo"], r["carga"]), r["modo_cpu"]): num(r["cpu_es_pct"]) for r in x2},
               "% do tempo de CPU", log=True)
        feitos.append("X2")

    x3 = [r for r in po if r["experimento"] == "X3" and r["operacao"] in ("open", "read", "write", "create")]
    if x3:
        ops = list(OrderedDict.fromkeys(r["operacao"] for r in x3))
        barras(plt, "X3_tempo_por_operacao.png", "X3 — tempo médio por operação", ops,
               ["compilador", "banco_dados"], {(r["operacao"], r["carga"]): num(r["tempo_medio_ms"]) for r in x3}, "ms")
        feitos.append("X3")

    x4 = [r for r in po if r["experimento"] == "X4" and r["operacao"] == "open"]
    if x4:
        linhas(plt, "X4_open_por_profundidade.png", "X4 — custo do open conforme a profundidade",
               {"acessos por open": [(int(r["carga"].split("_")[1]), num(r["acessos_medios"])) for r in x4],
                "tempo por open (ms)": [(int(r["carga"].split("_")[1]), num(r["tempo_medio_ms"])) for r in x4]},
               "profundidade (diretórios)", "valor")
        feitos.append("X4")

    x5 = [r for r in fs if r["experimento"] == "X5"]
    if x5:
        r = x5[0]
        cols = ["max_tabela_global", "max_tabela_processo", "max_soma_tabelas_processo", "max_contador_aberturas"]
        barras(plt, "X5_tabelas.png", "X5 — tabelas de arquivos abertos", cols, ["servidor_web"],
               {(c, "servidor_web"): num(r[c]) for c in cols}, "entradas")
        feitos.append("X5")

    x6 = [r for r in es if r["experimento"] == "X6" and r["cache"] != "nenhuma"]
    if x6:
        series = {}
        for r in x6:
            if r["escrita"] == "write-back":
                series.setdefault(r["cache"], []).append((num(r["capacidade_cache"]), num(r["acerto_cache_pct"])))
        linhas(plt, "X6_acerto.png", "X6 — taxa de acerto × capacidade", series, "capacidade (blocos)", "% de acertos")
        series = {}
        for r in x6:
            if r["cache"] == "LRU":
                series.setdefault("escritas físicas (%s)" % r["escrita"], []).append((num(r["capacidade_cache"]), num(r["escritas_fisicas"])))
                series.setdefault("perdidos na queda (%s)" % r["escrita"], []).append((num(r["capacidade_cache"]), num(r["perdidos_na_queda"])))
        linhas(plt, "X6_escrita.png", "X6 — write-through × write-back (LRU)", series, "capacidade (blocos)", "blocos")
        feitos.append("X6")

    x7 = [r for r in es if r["experimento"] == "X7"]
    if x7:
        for met, rot in (("resposta_p95_ms", "resposta no percentil 95 (ms)"), ("espera_max_ms", "maior espera (ms)")):
            series = {}
            for r in x7:
                series.setdefault(r["escalonador"], []).append((1000.0 / num(r["intervalo_medio_ms"]), num(r[met])))
            linhas(plt, "X7_%s.png" % met, "X7 — %s" % rot, series, "taxa de chegada (req/s)", rot)
        feitos.append("X7")

    x8 = [r for r in es if r["experimento"] == "X8"]
    if x8:
        nbs = list(OrderedDict.fromkeys(r["n_blocos_req"] for r in x8))
        barras(plt, "X8_cpu.png", "X8 — CPU gasta com E/S × tamanho da requisição", nbs,
               ["polling", "interrupcao", "dma"], {(r["n_blocos_req"], r["modo_cpu"]): num(r["cpu_es_pct"]) for r in x8},
               "% do tempo de CPU", log=True)
    if bf:
        series = {}
        for r in bf:
            series.setdefault("%s buffer(s)" % r["n_buffers"], []).append((num(r["consumo_ms"]), num(r["tempo_total_ms"])))
        linhas(plt, "X8_buffering.png", "X8 — buffering: tempo total × velocidade do dispositivo", series,
               "tempo para gravar um bloco (ms)", "tempo total (ms)")
        feitos.append("X8")

    x11 = [r for r in fs if r["experimento"] == "X11"]
    if x11:
        alocs = [r["alocador"] for r in x11]
        barras(plt, "X11_alocacao.png", "X11 — alocadores", ["acessos_por_op", "tempo_medio_op_ms"], alocs,
               {(c, r["alocador"]): num(r[c]) for r in x11 for c in ("acessos_por_op", "tempo_medio_op_ms")}, "valor")
        barras(plt, "X11_fragmentacao.png", "X11 — espaço livre e falhas", ["segmentos_livres", "falhas_alocacao", "realocacoes"],
               alocs, {(c, r["alocador"]): extra(r, c) for r in x11 for c in ("segmentos_livres", "falhas_alocacao", "realocacoes")},
               "quantidade")
        feitos.append("X11")

    x12 = [r for r in es if r["experimento"] == "X12"]
    if x12:
        grupos = list(OrderedDict.fromkeys("%s/%s" % (r["carga"], r["cache"]) for r in x12))
        barras(plt, "X12_resposta.png", "X12 — integração: tempo de resposta médio", grupos,
               ["FCFS", "SSTF", "SCAN"], {("%s/%s" % (r["carga"], r["cache"]), r["escalonador"]): num(r["resposta_media_ms"]) for r in x12},
               "ms", log=True)
        feitos.append("X12")

    print("Gráficos gerados em %s para: %s" % (SAIDA, ", ".join(feitos) or "nenhum experimento"))
    print("X9, X10 e X13 não têm gráfico padrão: apresentem tabelas no relatório.")


if __name__ == "__main__":
    main()
