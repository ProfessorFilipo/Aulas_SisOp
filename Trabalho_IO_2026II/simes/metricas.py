# -*- coding: utf-8 -*-
"""
Estatísticas e gravação dos resultados em CSV. FORNECIDO.

As colunas dos CSVs são fixas: não as alterem. Os gráficos e a validação da entrega
dependem delas.
"""
import csv
import math
import os

COLUNAS = {
    "es.csv": [
        "experimento", "carga", "escalonador", "dispositivo", "modo_cpu", "cache", "capacidade_cache",
        "escrita", "n_blocos_req", "intervalo_medio_ms", "requisicoes", "deslocamento_total",
        "tempo_total_ms", "resposta_media_ms", "resposta_p95_ms", "espera_max_ms", "vazao_req_s",
        "cpu_es_pct", "acerto_cache_pct", "escritas_fisicas", "perdidos_na_queda", "extras",
    ],
    "arquivos.csv": [
        "experimento", "carga", "alocador", "bloqueio", "operacoes", "erros", "acessos_total",
        "acessos_por_op", "tempo_total_ms", "tempo_medio_op_ms", "max_tabela_global",
        "max_tabela_processo", "max_soma_tabelas_processo", "max_contador_aberturas", "extras",
    ],
    "arquivos_por_operacao.csv": [
        "experimento", "carga", "alocador", "bloqueio", "operacao", "n", "erros", "acessos_medios",
        "tempo_medio_ms",
    ],
    "buffering.csv": [
        "experimento", "n_buffers", "producao_ms", "consumo_ms", "blocos", "tempo_total_ms",
        "bloqueio_produtor_ms", "utilizacao_dispositivo_pct",
    ],
    "experimentos.csv": ["experimento", "status", "execucoes", "detalhe"],
}


def media(valores):
    valores = list(valores)
    return sum(valores) / len(valores) if valores else 0.0


def percentil(valores, p):
    """Percentil p (0–100) pelo método do vizinho mais próximo."""
    valores = sorted(valores)
    if not valores:
        return 0.0
    k = max(0, int(math.ceil(p / 100.0 * len(valores))) - 1)
    return valores[k]


def formatar_extras(d):
    """{'a': 1, 'b': 2.5} -> 'a=1;b=2.5' (coluna 'extras' dos CSVs)."""
    if not d:
        return ""
    partes = []
    for k in sorted(d):
        v = d[k]
        if isinstance(v, float):
            v = round(v, 4)
        partes.append("%s=%s" % (k, v))
    return ";".join(partes)


class GravadorCSV:
    """Acumula linhas por arquivo e grava tudo em uma pasta (sobrescreve)."""

    def __init__(self, pasta):
        self.pasta = pasta
        self.linhas = {nome: [] for nome in COLUNAS}

    def adicionar(self, arquivo, linha):
        colunas = COLUNAS[arquivo]
        faltando = [c for c in colunas if c not in linha]
        if faltando:
            raise KeyError("colunas faltando em %s: %s" % (arquivo, faltando))
        self.linhas[arquivo].append({c: _fmt(linha[c]) for c in colunas})

    def gravar(self):
        os.makedirs(self.pasta, exist_ok=True)
        for arquivo, linhas in self.linhas.items():
            with open(os.path.join(self.pasta, arquivo), "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=COLUNAS[arquivo])
                w.writeheader()
                w.writerows(linhas)


def _fmt(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "sim" if v else "nao"
    if isinstance(v, float):
        return "%.4f" % v
    return v
