#!/usr/bin/env python3
"""Tópico 13.6 — STREAMS e a ideia de 'módulos' entre o driver e o processo.

O Linux e o macOS não implementam STREAMS, mas o driver de terminal tem uma
camada intermediária equivalente ao exemplo do livro: a disciplina de linha,
que faz a edição da entrada (backspace, Enter...) antes de entregar os dados.

Gestão de Entrada e Saída — Sistemas Operacionais (PUCRS)
Prof. Filipo Novo Mór - filipomor.com - github.com/ProfessorFilipo
"""
import os
import sys
import termios
import tty

from comum import LINUX, nota, titulo

if not sys.stdin.isatty():
    sys.exit("Rode este exemplo diretamente num terminal.")

titulo("1. COM o módulo de edição de linha (modo canônico)")
print("Digite uma palavra, apague letras com Backspace e tecle Enter:")
linha = input("> ")
print("O programa recebeu só a linha final, já editada: %r" % linha)

titulo("2. SEM o módulo de edição (modo não canônico)")
print("Agora cada tecla chega ao programa no instante em que é digitada.")
print("Teste letras, Backspace e as setas. Tecle 'q' para sair.\n")
fd = sys.stdin.fileno()
original = termios.tcgetattr(fd)
try:
    tty.setcbreak(fd)                 # retira a edição de linha e o eco
    while True:
        byte = os.read(fd, 1)
        print("  recebi o byte 0x%02x  %r" % (byte[0], byte), flush=True)
        if byte == b"q":
            break
finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, original)   # devolve o terminal ao normal
nota("Backspace chega como 0x7f: quem 'apagava' a letra era o módulo, não o programa")
if LINUX:
    with open("/proc/tty/ldiscs") as f:
        print("\nDisciplinas de linha disponíveis neste kernel (/proc/tty/ldiscs):")
        for linha in f.read().splitlines()[:6]:
            print("   " + linha)
