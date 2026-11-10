# -*- coding: utf-8 -*-
"""
Gera as cargas padronizadas da pasta cargas/ (sementes fixas). FORNECIDO.

As cargas já vêm prontas no repositório; este script só serve para conferir como foram
geradas ou para criar cargas extras (use OUTRA pasta e outra semente, e declare no relatório).

Uso:  python gerar_cargas.py [pasta_destino]
"""
import os
import sys

from simes.cargas import gerar_es, gravar_carga_es
from simes.cargas_arquivos import PADRONIZADAS, fs_profundidade

CARGAS_ES = {
    "es_sequencial": dict(tipo="sequencial"),
    "es_aleatoria": dict(tipo="aleatoria"),
    "es_concentrada": dict(tipo="concentrada"),
    "es_rajadas": dict(tipo="rajadas"),
    "es_reuso": dict(tipo="reuso", n=3000, intervalo_medio_ms=8.0, fracao_leitura=0.65),
}


def main():
    destino = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "cargas")
    os.makedirs(destino, exist_ok=True)
    for nome, kw in CARGAS_ES.items():
        reqs = gerar_es(**kw)
        gravar_carga_es(reqs, os.path.join(destino, nome + ".txt"),
                        "Carga padronizada %s (gerar_es %s, semente 2026)" % (nome, kw))
        print("%-22s %6d requisições" % (nome, len(reqs)))
    for nome, funcao in PADRONIZADAS.items():
        linhas = funcao()
        with open(os.path.join(destino, nome + ".txt"), "w", encoding="utf-8") as f:
            f.write("# Carga padronizada %s (semente 2026)\n# tempo_ms processo operacao argumentos\n" % nome)
            f.write("\n".join(linhas) + "\n")
        print("%-22s %6d operações" % (nome, len(linhas)))
    with open(os.path.join(destino, "fs_profundidade_exemplo.txt"), "w", encoding="utf-8") as f:
        f.write("# Exemplo da carga do X4 com profundidade 5 (o X4 gera as profundidades 1 a 10)\n")
        f.write("\n".join(fs_profundidade(5)) + "\n")


if __name__ == "__main__":
    main()
