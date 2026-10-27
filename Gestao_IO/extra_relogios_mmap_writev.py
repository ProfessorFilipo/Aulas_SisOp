#!/usr/bin/env python3
"""Extras para estudo em casa — relógios (13.3.3), arquivos mapeados em memória (13.3.1)
e E/S vetorizada (13.3.5).

Gestão de Entrada e Saída — Sistemas Operacionais (PUCRS)
Prof. Filipo Novo Mór - filipomor.com - github.com/ProfessorFilipo
"""
import mmap
import os
import time

from comum import nota, titulo

titulo("1. Relógios e temporizadores")
for nome in ("time", "monotonic", "perf_counter"):
    info = time.get_clock_info(nome)
    print("%-13s implementação: %-38s resolução: %.0e s" % (nome, info.implementation, info.resolution))
pedidos, total = 200, 0.0
for _ in range(pedidos):
    t0 = time.perf_counter()
    time.sleep(0.001)                         # "acorde-me daqui a 1 ms"
    total += time.perf_counter() - t0
print("\nPedi para dormir 1,000 ms; em média dormi %.3f ms" % (total / pedidos * 1000))
nota("o atraso extra vem da resolução do temporizador e do custo de acordar o processo")

titulo("2. Arquivo mapeado em memória (mmap)")
with open("mapeado.bin", "wb") as f:
    f.write(b"." * 4096)
with open("mapeado.bin", "r+b") as f:
    memoria = mmap.mmap(f.fileno(), 0)
    memoria[0:12] = b"ESCRITO-RAM!"           # escrita comum na memória, sem write()
    memoria.flush()
    memoria.close()
with open("mapeado.bin", "rb") as f:
    print("read() do arquivo devolve: %r" % f.read(20))
os.remove("mapeado.bin")
nota("a E/S foi feita pelo mesmo mecanismo de paginação da memória virtual")

titulo("3. E/S vetorizada (scatter-gather)")
partes = [b"Sistemas ", b"Operacionais ", b"- PUCRS\n"]
n = os.writev(1, partes)                      # 3 buffers, 1 única chamada de sistema
print("writev() gravou %d bytes de %d buffers numa só chamada" % (n, len(partes)))
