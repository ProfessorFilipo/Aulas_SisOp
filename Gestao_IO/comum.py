#!/usr/bin/env python3
"""Funções auxiliares usadas por todos os exemplos da aula de E/S.

Os exemplos funcionam em Linux (Ubuntu/Debian) e macOS (Intel ou Apple Silicon).
Só usam a biblioteca padrão do Python (3.8 ou mais recente).

Gestão de Entrada e Saída — Sistemas Operacionais (PUCRS)
Prof. Filipo Novo Mór - filipomor.com - github.com/ProfessorFilipo
"""
import platform
import shutil
import subprocess
import sys

SISTEMA = platform.system()        # 'Linux' ou 'Darwin' (macOS)
ARQUITETURA = platform.machine()   # 'x86_64', 'arm64' ou 'aarch64'
LINUX = SISTEMA == "Linux"
MAC = SISTEMA == "Darwin"
X86 = ARQUITETURA in ("x86_64", "AMD64", "i386", "i686")
ARM = ARQUITETURA in ("arm64", "aarch64")

if not (LINUX or MAC):
    sys.exit("Estes exemplos foram feitos para Linux (Ubuntu/Debian) e macOS.")


def nome_sistema():
    if MAC:
        return "macOS " + platform.mac_ver()[0]
    try:
        with open("/etc/os-release") as f:
            for linha in f:
                if linha.startswith("PRETTY_NAME="):
                    return linha.split("=", 1)[1].strip().strip('"')
    except OSError:
        pass
    return "Linux"


def titulo(texto):
    print()
    print("=" * 72)
    print(texto)
    print("=" * 72)


def nota(texto):
    print("  [nota] " + texto)


def rodar(cmd, max_linhas=None, mostrar=True):
    """Executa um comando e devolve sua saída; avisa se ele não existir."""
    if shutil.which(cmd[0]) is None:
        nota("o comando '%s' não está disponível nesta máquina" % cmd[0])
        return ""
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       universal_newlines=True)
    if mostrar:
        print("$ " + " ".join(cmd))
        linhas = r.stdout.rstrip().splitlines()
        if max_linhas is not None and len(linhas) > max_linhas:
            linhas = linhas[:max_linhas] + ["  ... (%d linhas omitidas)" % (len(r.stdout.splitlines()) - max_linhas)]
        for linha in linhas:
            print("  " + linha)
    return r.stdout


def pausa(msg="Pressione Enter para continuar..."):
    try:
        input("\n" + msg)
    except EOFError:
        pass
