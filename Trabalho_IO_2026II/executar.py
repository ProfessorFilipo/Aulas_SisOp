# -*- coding: utf-8 -*-
"""
SimES — ponto de entrada. FORNECIDO.

Exemplos (no Windows, troquem python3 por py):

  python3 executar.py es --carga cargas/es_aleatoria.txt --escalonador SSTF
  python3 executar.py es --carga cargas/es_reuso.txt --cache LRU --capacidade 512 --escrita write-back --queda 12000
  python3 executar.py arquivos --carga cargas/fs_compilador.txt
  python3 executar.py arquivos --carga cargas/fs_alocacao.txt --alocador indexada --blocos 20000
  python3 executar.py buffering --buffers 2 --producao 2 --consumo 8 --blocos 500
  python3 executar.py experimentos            (roda X1 a X13 e grava resultados/)
  python3 executar.py experimentos X1 X3      (só alguns)
  python3 executar.py testes                  (testes automáticos)
"""
import argparse
import os
import sys
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)


def cmd_es(a):
    from simes.cargas import ler_carga_es
    from simes.disco import criar_disco
    from simes.es.cache import criar_cache
    from simes.es.escalonadores import criar_escalonador
    from simes.es.simulador import simular_es
    reqs = ler_carga_es(a.carga)
    cache = criar_cache(a.cache, a.capacidade, a.escrita) if a.cache else None
    res = simular_es(reqs, criar_escalonador(a.escalonador), criar_disco(a.dispositivo), a.modo,
                     cache=cache, queda_ms=a.queda)
    for k, v in res.items():
        if k != "concluidas":
            print("%-22s %s" % (k, "%.3f" % v if isinstance(v, float) else v))


def cmd_arquivos(a):
    from simes.cargas import ler_carga_arquivos
    from simes.arquivos.simulador import montar_sistema, simular_arquivos
    sistema = montar_sistema(a.alocador, total_blocos=a.blocos, bloqueio=a.bloqueio)
    res = simular_arquivos(ler_carga_arquivos(a.carga), sistema)
    for k, v in res.items():
        if k not in ("por_operacao", "extras"):
            print("%-28s %s" % (k, "%.3f" % v if isinstance(v, float) else v))
    print("extras:", res["extras"])
    print("\n%-10s %6s %6s %14s %14s" % ("operação", "n", "erros", "acessos/op", "tempo médio ms"))
    for op, r in res["por_operacao"].items():
        print("%-10s %6d %6d %14.2f %14.3f" % (op, r["n"], r["erros"], r["acessos_medios"], r["tempo_medio_ms"]))


def cmd_buffering(a):
    from simes.es.buffering import simular_buffering
    print(simular_buffering(a.buffers, a.producao, a.consumo, a.blocos))


def cmd_experimentos(a):
    import experimentos
    experimentos.executar(a.lista or None)


def cmd_testes(a):
    suite = unittest.defaultTestLoader.discover(os.path.join(AQUI, "testes"), top_level_dir=AQUI)
    resultado = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if resultado.wasSuccessful() else 1)


def main():
    from simes import parametros as P
    ap = argparse.ArgumentParser(description="SimES — simulador de E/S e de sistema de arquivos")
    sub = ap.add_subparsers(dest="comando")
    sub.required = True

    p = sub.add_parser("es", help="simula uma carga de E/S de blocos")
    p.add_argument("--carga", required=True)
    p.add_argument("--escalonador", default="FCFS")
    p.add_argument("--dispositivo", default="hdd", choices=["hdd", "rapido", "flash"])
    p.add_argument("--modo", default="interrupcao", choices=["polling", "interrupcao", "dma"])
    p.add_argument("--cache", choices=["LRU", "FIFO"])
    p.add_argument("--capacidade", type=int, default=512)
    p.add_argument("--escrita", default="write-back", choices=["write-through", "write-back"])
    p.add_argument("--queda", type=float, help="instante (ms) de uma queda de energia simulada")
    p.set_defaults(funcao=cmd_es)

    p = sub.add_parser("arquivos", help="simula uma carga do sistema de arquivos")
    p.add_argument("--carga", required=True)
    p.add_argument("--alocador", default="contigua", choices=["contigua", "encadeada", "fat", "indexada"])
    p.add_argument("--bloqueio", default="consultivo", choices=["consultivo", "mandatorio"])
    p.add_argument("--blocos", type=int, default=P.TOTAL_BLOCOS, help="tamanho da partição em blocos")
    p.set_defaults(funcao=cmd_arquivos)

    p = sub.add_parser("buffering", help="simula produtor e dispositivo com n buffers (M3)")
    p.add_argument("--buffers", type=int, default=2)
    p.add_argument("--producao", type=float, default=2.0)
    p.add_argument("--consumo", type=float, default=2.0)
    p.add_argument("--blocos", type=int, default=500)
    p.set_defaults(funcao=cmd_buffering)

    p = sub.add_parser("experimentos", help="roda os experimentos X1-X13 e grava resultados/")
    p.add_argument("lista", nargs="*")
    p.set_defaults(funcao=cmd_experimentos)

    p = sub.add_parser("testes", help="roda os testes automáticos da pasta testes/")
    p.set_defaults(funcao=cmd_testes)

    a = ap.parse_args()
    a.funcao(a)


if __name__ == "__main__":
    main()
