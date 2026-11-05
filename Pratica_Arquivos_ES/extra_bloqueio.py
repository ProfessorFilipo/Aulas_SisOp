# -*- coding: utf-8 -*-
"""
Desafio extra — Bloqueio de arquivos: consultivo × mandatório
Conceitos: file locking, lock exclusivo, bloqueio consultivo (advisory) e mandatório.
Silberschatz, 9ª ed.: 11.1.2 (File Locking) e Lista, Questão 8

O script cria um processo A que trava o arquivo. Este processo (B) tenta usá-lo.
"""
import subprocess

from comum import *

TAMANHO = 64


def travar(fd, bloqueante=True):
    if WINDOWS:
        import msvcrt
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_LOCK if bloqueante else msvcrt.LK_NBLCK, TAMANHO)
    else:
        import fcntl
        fcntl.lockf(fd, fcntl.LOCK_EX | (0 if bloqueante else fcntl.LOCK_NB), TAMANHO, 0)


def processo_a(caminho):
    fd = os.open(caminho, os.O_RDWR | O_BINARY)
    travar(fd)
    print("travado", flush=True)
    sys.stdin.readline()          # segura o lock até o B mandar uma linha
    os.close(fd)


def main():
    estacao("extra", "Bloqueio de arquivos: consultivo × mandatório", "11.1.2")
    d = pasta("extra")
    arq = os.path.join(d, "conta.txt")
    with open(arq, "wb") as f:
        f.write(b"saldo=1000".ljust(TAMANHO, b" "))

    passo("1. O processo A trava os primeiros %d bytes do arquivo (lock exclusivo)" % TAMANHO)
    a = subprocess.Popen([sys.executable, os.path.abspath(__file__), "--segurar", arq],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    mostrar("Processo A diz:", a.stdout.readline().strip())
    mecanismo = "msvcrt.locking() -> LockFile" if WINDOWS else "fcntl.lockf() -> fcntl(F_SETLK)"
    mostrar("Mecanismo usado:", mecanismo)

    fd = os.open(arq, os.O_RDWR | O_BINARY)
    passo("2. B PEDE o lock")
    prever("Se B pedir o mesmo lock (sem esperar), ele consegue?")
    try:
        travar(fd, bloqueante=False)
        mostrar("B conseguiu o lock:", "SIM")
    except OSError as e:
        mostrar("B conseguiu o lock:", "NÃO -> " + descrever_erro(e))

    passo("3. B IGNORA o lock e escreve direto")
    prever("E se B simplesmente IGNORAR o lock e gravar 'saldo=0' no arquivo? O sistema impede?")
    try:
        os.lseek(fd, 0, os.SEEK_SET)
        os.write(fd, b"saldo=0   ")
        mostrar("Escrita de B:", "FUNCIONOU (o lock foi ignorado)")
    except OSError as e:
        mostrar("Escrita de B:", "BLOQUEADA PELO SO -> " + descrever_erro(e))
    os.close(fd)
    a.stdin.write("pode soltar\n")
    a.stdin.flush()
    a.wait()
    with open(arq, "rb") as f:
        mostrar("Conteúdo final:", repr(f.read().strip().decode()))

    discutir("O bloqueio que vocês viram é consultivo ou mandatório? Como sabem?",
             "Em um servidor de banco de dados, qual dos dois protege contra um programa mal escrito? (Questão 8)",
             "O Linux removeu o bloqueio mandatório no kernel 5.15. Pesquisem: por quê?")
    fim("99_limpar.py")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--segurar":
        processo_a(sys.argv[2])
    else:
        main()
