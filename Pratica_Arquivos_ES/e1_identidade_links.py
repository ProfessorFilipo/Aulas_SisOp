# -*- coding: utf-8 -*-
"""
Estação 1 — Identidade do arquivo e links
Conceitos: atributos (nome × identificador), diretório como tabela de símbolos,
grafo acíclico, hard link × link simbólico, contagem de referências.
Silberschatz, 9ª ed.: 11.1.1, 11.3.4 (Acyclic-Graph Directories)
"""
import shutil
import time

from comum import *


def ficha(caminho, rotulo, seguir=True):
    s = os.stat(caminho) if seguir else os.lstat(caminho)
    print("   %-18s ID=%-12s volume=%-12s links=%-3s %s  %6d B  mod. %s" % (
        rotulo, s.st_ino, s.st_dev, s.st_nlink, stat.filemode(s.st_mode),
        s.st_size, time.strftime("%H:%M:%S", time.localtime(s.st_mtime))))
    registrar("- %s: ID=%s volume=%s links=%s modo=%s tamanho=%s"
              % (rotulo, s.st_ino, s.st_dev, s.st_nlink, stat.filemode(s.st_mode), s.st_size))
    return s


def juncao_windows():
    """Junção de diretório: um 'link' para pastas que o Windows permite sem privilégio."""
    os.mkdir("pasta_alvo")
    open(os.path.join("pasta_alvo", "dentro.txt"), "w").write("arquivo dentro da pasta alvo\n")
    cod, out = rodar("mklink /J juncao pasta_alvo")
    if cod != 0:
        mostrar("mklink /J falhou:", out.strip())
        return
    mostrar("mklink /J juncao pasta_alvo:", "ok")
    mostrar("O que a junção guarda (readlink):", repr(os.readlink("juncao")))
    mostrar("Pela junção, juncao\\dentro.txt existe?", os.path.exists(os.path.join("juncao", "dentro.txt")))
    prever("Se apagarmos pasta_alvo, o que acontece com a junção?")
    shutil.rmtree("pasta_alvo")
    mostrar("A junção ainda existe (lexists)?", os.path.lexists("juncao"))
    mostrar("O alvo dela existe (exists)?", os.path.exists("juncao"))
    rodar("rmdir juncao")


def main():
    estacao(1, "Identidade do arquivo e links", "11.1.1 e 11.3.4")
    d = pasta("e1")
    os.chdir(d)

    passo("1. Criando o arquivo original.txt e lendo seus atributos")
    with open("original.txt", "w", encoding="utf-8") as f:
        f.write("Conteúdo do arquivo da estação 1.\n")
    time.sleep(1.1)
    s0 = ficha("original.txt", "original.txt")
    nota("ID = identificador interno (número do inode no Linux/macOS, File ID no NTFS).\n"
         "links = quantas entradas de diretório apontam para esses dados.")
    comando_nativo(linux="ls -li ; stat original.txt",
                   mac="ls -li ; stat -x original.txt",
                   windows="fsutil file queryfileid original.txt   (pode pedir Administrador)")

    passo("2. Renomear")
    prever("Ao renomear original.txt para renomeado.txt, o ID muda? E a data de modificação?")
    os.rename("original.txt", "renomeado.txt")
    s1 = ficha("renomeado.txt", "renomeado.txt")
    mostrar("O ID mudou?", "SIM" if s1.st_ino != s0.st_ino else "NÃO")
    mostrar("A data de modificação mudou?", "SIM" if s1.st_mtime != s0.st_mtime else "NÃO")

    passo("3. Copiar")
    prever("E se copiarmos renomeado.txt para copia.txt (cópia que preserva datas)? Mesmo ID?")
    shutil.copy2("renomeado.txt", "copia.txt")
    s2 = ficha("copia.txt", "copia.txt")
    mostrar("Mesmo ID do renomeado.txt?", "SIM" if s2.st_ino == s1.st_ino else "NÃO")

    passo("4. Link rígido (hard link)")
    prever("Criaremos o hard link rigido.txt -> renomeado.txt. "
           "Quantos links o arquivo terá? O ID do link será diferente?")
    try:
        os.link("renomeado.txt", "rigido.txt")
        ficha("renomeado.txt", "renomeado.txt")
        ficha("rigido.txt", "rigido.txt")
    except OSError as e:
        mostrar("Falhou:", descrever_erro(e))
    comando_nativo(linux="ln renomeado.txt rigido.txt", mac="ln renomeado.txt rigido.txt",
                   windows="mklink /H rigido.txt renomeado.txt")

    passo("5. Link simbólico (symlink)")
    prever("Criaremos o link simbólico simbolico.txt -> renomeado.txt. "
           "Ele terá o mesmo ID do arquivo? O que ele guarda dentro?")
    tem_simbolico = False
    try:
        os.symlink("renomeado.txt", "simbolico.txt")
        tem_simbolico = True
        ficha("simbolico.txt", "simbolico (lstat)", seguir=False)
        ficha("simbolico.txt", "simbolico (stat)")
        mostrar("Conteúdo do link (readlink):", repr(os.readlink("simbolico.txt")))
        nota("lstat = atributos do próprio link; stat = atributos do alvo (segue o link).")
    except OSError as e:
        mostrar("Falhou:", descrever_erro(e))
        if WINDOWS:
            nota("No Windows, criar links simbólicos exige o privilégio SeCreateSymbolicLinkPrivilege\n"
                 "(Administrador ou Modo de Desenvolvedor). Anotem: por que o Windows restringe isso?\n"
                 "Como alternativa sem privilégio, vamos usar uma JUNÇÃO de diretório (mklink /J).")
            juncao_windows()
    comando_nativo(linux="ln -s renomeado.txt simbolico.txt", mac="ln -s renomeado.txt simbolico.txt",
                   windows="mklink simbolico.txt renomeado.txt")

    passo("6. Apagar o arquivo 'original' (renomeado.txt)")
    prever("Depois de apagar renomeado.txt: dá para ler pelo hard link? E pelo link simbólico? "
           "Quantos links sobram?")
    os.remove("renomeado.txt")
    try:
        with open("rigido.txt", encoding="utf-8") as f:
            mostrar("Leitura por rigido.txt:", repr(f.read().strip()))
        ficha("rigido.txt", "rigido.txt")
    except OSError as e:
        mostrar("Leitura por rigido.txt falhou:", descrever_erro(e))
    if tem_simbolico:
        mostrar("simbolico.txt ainda existe (lexists)?", os.path.lexists("simbolico.txt"))
        mostrar("O alvo dele existe (exists)?", os.path.exists("simbolico.txt"))
        try:
            open("simbolico.txt").read()
            mostrar("Leitura por simbolico.txt:", "funcionou")
        except OSError as e:
            mostrar("Leitura por simbolico.txt falhou:", descrever_erro(e))

    discutir("Quem guarda o NOME do arquivo: o próprio arquivo ou o diretório?",
             "Quando os blocos de dados são liberados de fato? Que estrutura o kernel consulta?",
             "Por que um link simbólico pode ficar 'pendente' e um hard link não? (Lista, Questão 2)",
             "Por que, em geral, não se permite hard link para diretórios? (Lista, Questão 6)")
    fim("e2_arquivo_aberto.py")


if __name__ == "__main__":
    main()
