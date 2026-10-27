#!/usr/bin/env python3
"""Tópico 13.7 — Desempenho: o custo de atravessar a fronteira usuário/kernel.

Copia 1 MiB de /dev/zero para /dev/null com blocos de tamanhos diferentes.
A quantidade de dados é sempre a mesma; só muda o número de chamadas de sistema.

Gestão de Entrada e Saída — Sistemas Operacionais (PUCRS)
Prof. Filipo Novo Mór - filipomor.com - github.com/ProfessorFilipo
"""
import resource
import subprocess
import time

from comum import nota, titulo

TOTAL = 1 << 20     # 1 MiB


def medir(bloco):
    antes = resource.getrusage(resource.RUSAGE_CHILDREN)
    t0 = time.perf_counter()
    subprocess.run(["dd", "if=/dev/zero", "of=/dev/null", "bs=%d" % bloco,
                    "count=%d" % (TOTAL // bloco)], stderr=subprocess.DEVNULL, check=True)
    tempo = time.perf_counter() - t0
    depois = resource.getrusage(resource.RUSAGE_CHILDREN)
    return tempo, depois.ru_utime - antes.ru_utime, depois.ru_stime - antes.ru_stime


titulo("Copiando 1 MiB com blocos de tamanhos diferentes (comando dd)")
print("%10s %14s %10s %13s %13s" % ("bloco", "chamadas", "tempo", "CPU (usuário)", "CPU (kernel)"))
for bloco in (1, 16, 512, 4096, 1 << 20):
    tempo, usr, sis = medir(bloco)
    chamadas = 2 * TOTAL // bloco          # um read() e um write() por bloco
    print("%9dB %14s %9.3fs %12.3fs %12.3fs" % (bloco, format(chamadas, ",").replace(",", "."),
                                               tempo, usr, sis))
nota("mesmos dados, milhares de vezes mais chamadas: cada uma troca de modo usuário <-> kernel")
nota("princípio do livro: reduzir o número de transferências usando blocos maiores")
