#!/usr/bin/env python3
"""Tópico 13.3 — Dispositivos de bloco e de caractere, números <major, minor> e ioctl().

Gestão de Entrada e Saída — Sistemas Operacionais (PUCRS)
Prof. Filipo Novo Mór - filipomor.com - github.com/ProfessorFilipo
"""
import fcntl
import glob
import os
import signal
import stat
import struct
import sys
import termios
import time

from comum import LINUX, MAC, nota, titulo


def disco_principal():
    if MAC:
        return ["/dev/disk0", "/dev/rdisk0"]   # rdisk = acesso "raw" (seção 13.3.1)
    for nome in sorted(os.listdir("/sys/block")):
        if not nome.startswith(("loop", "ram", "zram", "sr", "fd", "dm-", "md")):
            return ["/dev/" + nome]
    return []


titulo("1. Dispositivos são arquivos especiais em /dev")
print("%-14s %-10s %-12s %s" % ("arquivo", "tipo", "<maj, min>", "permissões"))
for caminho in disco_principal() + ["/dev/null", "/dev/zero", "/dev/urandom", "/dev/tty"]:
    try:
        st = os.stat(caminho)
    except OSError:
        continue
    tipo = "BLOCO" if stat.S_ISBLK(st.st_mode) else "CARACTERE" if stat.S_ISCHR(st.st_mode) else "?"
    print("%-14s %-10s <%3d, %3d>   %s" % (caminho, tipo, os.major(st.st_rdev),
                                          os.minor(st.st_rdev), stat.filemode(st.st_mode)))
nota("major identifica o DRIVER; minor identifica o dispositivo para esse driver")
if LINUX:
    nota("tabela de majors do kernel: cat /proc/devices")

titulo("2. ioctl(): a 'porta dos fundos' para comandos específicos do driver")
if not sys.stdout.isatty():
    sys.exit("Rode este exemplo diretamente num terminal.")
ARG = struct.pack("HHHH", 0, 0, 0, 0)


def tamanho_terminal():
    fd = sys.stdout.fileno()
    # ioctl(descritor, comando, ponteiro p/ estrutura): os 3 argumentos do livro
    resp = fcntl.ioctl(fd, termios.TIOCGWINSZ, ARG)
    linhas, colunas, _, _ = struct.unpack("HHHH", resp)
    return linhas, colunas


print("ioctl(1, TIOCGWINSZ, &estrutura) -> %d linhas x %d colunas" % tamanho_terminal())

DURACAO = 10
print("\nRedimensione a janela do terminal nos próximos %d segundos!" % DURACAO)
print("(o driver do terminal avisa o processo com o sinal SIGWINCH)\n")


def ao_redimensionar(sig, frame):
    print("  SIGWINCH recebido -> novo tamanho: %d linhas x %d colunas" % tamanho_terminal())


signal.signal(signal.SIGWINCH, ao_redimensionar)
fim = time.time() + DURACAO
try:
    while time.time() < fim:
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
print("Fim.")
