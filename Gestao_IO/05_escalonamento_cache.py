#!/usr/bin/env python3
"""Tópico 13.4.1 a 13.4.3 — Escalonamento de E/S, buffering/caching e escrita adiada.

Gestão de Entrada e Saída — Sistemas Operacionais (PUCRS)
Prof. Filipo Novo Mór - filipomor.com - github.com/ProfessorFilipo
"""
import glob
import os
import random
import subprocess
import time

from comum import LINUX, MAC, nota, titulo

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO = os.path.join(PASTA, "dados_teste.bin")
ESCRITA = os.path.join(PASTA, "escrita_teste.bin")
TAMANHO_MB = 128

titulo("1. Escalonamento de E/S: a ordem dos pedidos importa (exemplo da seção 13.4.1)")
cabeca = 0
pedidos = [("aplicação 1", 9000, "fim do disco"),
           ("aplicação 2", 100, "início do disco"),
           ("aplicação 3", 5000, "meio do disco")]


def percurso(ordem):
    pos, total = cabeca, 0
    for _, bloco, _ in ordem:
        total += abs(bloco - pos)
        pos = bloco
    return total


print("Ordem de chegada (1, 2, 3): o braço percorre %5d blocos" % percurso(pedidos))
reordenado = sorted(pedidos, key=lambda p: p[1])
print("Ordem reorganizada (2, 3, 1): o braço percorre %5d blocos" % percurso(reordenado))
if LINUX:
    print("\nEscalonador ativo em cada disco deste computador (entre colchetes):")
    for arq in sorted(glob.glob("/sys/block/*/queue/scheduler")):
        disco = arq.split("/")[3]
        if not disco.startswith(("loop", "ram", "zram")):
            print("   %-10s %s" % (disco, open(arq).read().strip()))
elif MAC:
    nota("o macOS não expõe o escalonador; ele prioriza E/S por processo (comando taskpolicy)")

titulo("2. Cache de leitura: as mesmas leituras feitas duas vezes")
if not os.path.exists(ARQUIVO) or os.path.getsize(ARQUIVO) != TAMANHO_MB << 20:
    print("Criando %s com %d MB (só na primeira execução)..." % (os.path.basename(ARQUIVO), TAMANHO_MB))
    with open(ARQUIVO, "wb") as f:
        for _ in range(TAMANHO_MB):
            f.write(os.urandom(1 << 20))


def esvaziar_cache():
    fd = os.open(ARQUIVO, os.O_RDONLY)
    os.fsync(fd)
    if LINUX:   # pede ao kernel que descarte as páginas deste arquivo (não precisa de root)
        os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
    os.close(fd)
    if MAC:     # no macOS só o 'purge' esvazia o cache, e ele exige senha de administrador
        print("macOS: esvaziando o cache com 'sudo purge' (digite sua senha se for pedida)")
        if subprocess.call(["sudo", "purge"]) != 0:
            nota("purge não executado: a 1ª passada pode não ter vindo do disco")


LEITURAS = 2000
random.seed(13)
posicoes = [random.randrange(TAMANHO_MB * 256) * 4096 for _ in range(LEITURAS)]


def passada():
    fd = os.open(ARQUIVO, os.O_RDONLY)
    t0 = time.perf_counter()
    for p in posicoes:
        os.pread(fd, 4096, p)          # lê 4 KB numa posição aleatória
    t = time.perf_counter() - t0
    os.close(fd)
    return t


esvaziar_cache()
fria, quente = passada(), passada()
print("%d leituras de 4 KB em posições aleatórias:" % LEITURAS)
print("  1ª passada (dados vêm do disco):        %7.3f s  (%6.1f µs por leitura)" % (fria, fria / LEITURAS * 1e6))
print("  2ª passada (dados vêm do cache na RAM): %7.3f s  (%6.1f µs por leitura)" % (quente, quente / LEITURAS * 1e6))
print("  -> o cache tornou a leitura %.0fx mais rápida" % (fria / quente))

titulo("3. Escrita adiada: write() retorna antes de o dado chegar ao disco")
N, BLOCO = 200, b"x" * 4096


def gravar(esperar_disco):
    t0 = time.perf_counter()
    with open(ESCRITA, "wb", buffering=0) as f:
        for _ in range(N):
            f.write(BLOCO)
            if esperar_disco:
                if MAC:   # no macOS, fsync() não esvazia o cache interno do SSD; F_FULLFSYNC sim
                    import fcntl
                    fcntl.fcntl(f.fileno(), getattr(fcntl, "F_FULLFSYNC", 51))
                else:
                    os.fsync(f.fileno())
    return time.perf_counter() - t0


sem = gravar(False)
com = gravar(True)
print("%d escritas de 4 KB, só no cache (write):          %8.4f s" % (N, sem))
print("%d escritas de 4 KB, esperando o disco (fsync):    %8.4f s  -> %.0fx mais lento"
      % (N, com, com / sem))
os.remove(ESCRITA)
if LINUX:
    with open("/proc/sys/vm/dirty_expire_centisecs") as f:
        cs = int(f.read())
    print("\nLinux: um dado 'sujo' fica no máximo %d s no cache antes de ir ao disco" % (cs // 100))
    nota("compare com os '30 segundos' citados no livro (seção 13.3.4)")
nota("apague %s ao final da aula para liberar %d MB" % (os.path.basename(ARQUIVO), TAMANHO_MB))
