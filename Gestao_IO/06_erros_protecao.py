#!/usr/bin/env python3
"""Tópico 13.4.5 e 13.4.6 — Tratamento de erros (errno) e proteção de E/S.

Gestão de Entrada e Saída — Sistemas Operacionais (PUCRS)
Prof. Filipo Novo Mór - filipomor.com - github.com/ProfessorFilipo
"""
import errno
import grp
import os
import pwd
import shutil
import stat
import subprocess
import tempfile

from comum import LINUX, MAC, nota, titulo

titulo("1. Erros de E/S: a chamada falha e o kernel informa um código (errno)")


def tentar(descricao, operacao):
    try:
        operacao()
        print("%-44s -> sucesso" % descricao)
    except OSError as e:
        print("%-44s -> errno %3d %-8s %s" % (descricao, e.errno, errno.errorcode.get(e.errno, "?"), e.strerror))


leitura, escrita = os.pipe()
os.set_blocking(leitura, False)
diretorio = os.open(".", os.O_RDONLY)
tentar("abrir um arquivo que não existe", lambda: os.open("/nao/existe.txt", os.O_RDONLY))
tentar("ler do lado de ESCRITA de um pipe", lambda: os.read(escrita, 10))
tentar("ler um diretório como se fosse arquivo", lambda: os.read(diretorio, 10))
tentar("ler um pipe vazio sem bloquear", lambda: os.read(leitura, 10))
nota("os nomes (ENOENT, EBADF...) são padrão POSIX; os números variam entre sistemas")

titulo("2. Proteção: um programa comum não acessa o disco diretamente")
disco = "/dev/rdisk0" if MAC else None
if LINUX:
    for nome in sorted(os.listdir("/sys/block")):
        if not nome.startswith(("loop", "ram", "zram", "sr", "fd", "dm-", "md")):
            disco = "/dev/" + nome
            break
if disco and os.path.exists(disco):
    st = os.stat(disco)
    print("%s  %s  dono=%s  grupo=%s" % (disco, stat.filemode(st.st_mode),
                                         pwd.getpwuid(st.st_uid).pw_name, grp.getgrgid(st.st_gid).gr_name))
    if os.geteuid() == 0:
        nota("você está como root: o kernel permitiria o acesso; rode sem sudo")
    else:
        tentar("abrir %s para leitura" % disco, lambda: os.close(os.open(disco, os.O_RDONLY)))
        nota("para ler o disco, o programa precisa pedir ao SO (chamada de sistema),")
        nota("que verifica as permissões antes de fazer a E/S")

titulo("3. Proteção: instruções que mexem no hardware são privilegiadas")
fonte = os.path.join(os.path.dirname(os.path.abspath(__file__)), "privilegiada.c")
if shutil.which("cc") is None:
    print("Compilador C não encontrado.")
    nota("macOS: xcode-select --install | Ubuntu/Debian: sudo apt install build-essential")
else:
    binario = os.path.join(tempfile.gettempdir(), "privilegiada_%d" % os.getuid())
    if subprocess.call(["cc", "-O0", fonte, "-o", binario]) == 0:
        subprocess.call([binario])
        nota("o processador recusou a instrução em modo usuário e avisou o kernel (exceção),")
        nota("que encerrou o programa: só o SO, em modo kernel, pode desligar interrupções")
