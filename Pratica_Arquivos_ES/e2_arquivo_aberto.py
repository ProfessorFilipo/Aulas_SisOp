# -*- coding: utf-8 -*-
"""
Estação 2 — O arquivo aberto: tabelas do kernel
Conceitos: open(), tabela de arquivos abertos por processo × tabela global,
ponteiro de posição (offset), dup(), contador de aberturas, apagar arquivo em uso.
Silberschatz, 9ª ed.: 11.1.2 (File Operations) e Lista, Questão 4
"""
from comum import *


def posicao(fd):
    return os.lseek(fd, 0, os.SEEK_CUR)


def ler(fd, n, rotulo):
    dados = os.read(fd, n)
    mostrar("%s leu %d bytes:" % (rotulo, len(dados)), repr(dados.decode()))
    return dados


def mostrar_tabela_linux(fds):
    """No Linux o kernel expõe a tabela do processo em /proc/self/fd e /proc/self/fdinfo."""
    for nome, fd in fds:
        try:
            alvo = os.readlink("/proc/self/fd/%d" % fd)
            with open("/proc/self/fdinfo/%d" % fd) as f:
                pos = [l.split()[1] for l in f if l.startswith("pos:")][0]
            mostrar("  /proc/self/fd/%d (%s)" % (fd, nome), "pos=%s -> %s" % (pos, alvo))
        except OSError:
            pass


def main():
    estacao(2, "O arquivo aberto: tabelas do kernel", "11.1.2")
    d = pasta("e2")
    os.chdir(d)
    caminho = os.path.join(d, "dados.txt")
    with open(caminho, "wb") as f:
        f.write(b"0123456789ABCDEFGHIJ")

    passo("1. Duas aberturas independentes do mesmo arquivo")
    fd_a = os.open(caminho, os.O_RDONLY | O_BINARY)
    fd_b = os.open(caminho, os.O_RDONLY | O_BINARY)
    mostrar("Descritores obtidos:", "fd_a=%d  fd_b=%d" % (fd_a, fd_b))
    ler(fd_a, 5, "fd_a")
    prever("Agora vamos ler 5 bytes por fd_b. Quais bytes virão?")
    ler(fd_b, 5, "fd_b")

    passo("2. Um descritor duplicado com dup()")
    fd_c = os.dup(fd_a)
    mostrar("fd_c = dup(fd_a) =", fd_c)
    prever("Lendo 5 bytes por fd_c (cópia de fd_a), quais bytes virão? "
           "E depois, lendo mais 5 por fd_a?")
    ler(fd_c, 5, "fd_c")
    ler(fd_a, 5, "fd_a")
    print()
    mostrar("Posição atual de fd_a:", posicao(fd_a))
    mostrar("Posição atual de fd_b:", posicao(fd_b))
    mostrar("Posição atual de fd_c:", posicao(fd_c))
    if LINUX:
        nota("O que o kernel do Linux mostra sobre este processo:")
        mostrar_tabela_linux([("fd_a", fd_a), ("fd_b", fd_b), ("fd_c", fd_c)])
    elif MAC:
        cod, out = rodar(["lsof", "-a", "-p", str(os.getpid()), "-d",
                          "%d,%d,%d" % (fd_a, fd_b, fd_c)])
        nota("lsof -p %d  (tabela de descritores deste processo: FD %d, %d e %d\n"
             "apontam para o mesmo arquivo, o mesmo NODE/inode):" % (os.getpid(), fd_a, fd_b, fd_c))
        mostrar_saida(out, 6)
    else:
        nota("No Windows, a tabela de handles de um processo pode ser vista no\n"
             "Process Explorer (Sysinternals): View > Lower Pane View > Handles.")
    os.close(fd_b)
    os.close(fd_c)

    passo("3. Apagar um arquivo que ainda está aberto")
    prever("fd_a continua aberto. Conseguimos apagar dados.txt? "
           "Se sim, ainda dá para ler o conteúdo por fd_a?")
    try:
        os.remove(caminho)
        mostrar("os.remove():", "funcionou")
        mostrar("O nome ainda existe na pasta?", os.path.exists(caminho))
        os.lseek(fd_a, 0, os.SEEK_SET)
        ler(fd_a, 100, "fd_a (depois de apagar)")
        mostrar("Links do arquivo (fstat):", os.fstat(fd_a).st_nlink)
        if LINUX:
            mostrar("/proc/self/fd/%d aponta para:" % fd_a, os.readlink("/proc/self/fd/%d" % fd_a))
        comando_nativo(linux="lsof +L1   (arquivos apagados que ainda estão abertos)",
                       mac="lsof +L1   (arquivos apagados que ainda estão abertos)")
    except OSError as e:
        mostrar("os.remove() falhou:", descrever_erro(e))
        if WINDOWS:
            nota("Por padrão, o Windows abre arquivos sem FILE_SHARE_DELETE:\n"
                 "enquanto houver um handle aberto, o nome não pode ser removido.")
    os.close(fd_a)
    mostrar("Depois de fechar fd_a, o arquivo existe?", os.path.exists(caminho))

    discutir("Que informação ficou na tabela POR PROCESSO e qual na tabela GLOBAL? (Lista, Questão 4)",
             "Por que fd_b não 'andou' quando lemos por fd_a, mas fd_c andou?",
             "Quando o kernel pode, de fato, liberar os blocos de um arquivo apagado?",
             "Como o Linux atualiza bibliotecas em uso sem reiniciar, e por que o Windows pede reinício?")
    fim("e3_buffers.py")


if __name__ == "__main__":
    main()
