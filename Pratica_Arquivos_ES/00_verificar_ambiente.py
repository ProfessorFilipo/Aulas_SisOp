# -*- coding: utf-8 -*-
"""
Verifica se a máquina está pronta para a atividade prática (Linux, macOS ou Windows).
Uso:  python3 00_verificar_ambiente.py      (no Windows:  py 00_verificar_ambiente.py)
"""
import tempfile

from comum import *

problemas = []


def ok(rotulo, valor=""):
    print("   [ ok ] %-36s %s" % (rotulo, valor))


def atencao(rotulo, valor=""):
    print(alerta("   [ !! ] %-36s %s" % (rotulo, valor)))
    problemas.append(rotulo)


def main():
    print(destaque("\n  VERIFICAÇÃO DO AMBIENTE — Atividade prática: Arquivos e E/S\n"))
    v = sys.version_info
    if v >= (3, 8):
        ok("Python", platform.python_version())
    else:
        atencao("Python 3.8 ou superior é necessário", platform.python_version())
    ok("Sistema operacional", "%s %s (%s)" % (NOME_SO, platform.release(), platform.machine()))
    if WINDOWS:
        ok("Versão do Windows", platform.version())
    elif MAC:
        ok("Versão do macOS", platform.mac_ver()[0])
    if eh_admin():
        print(alerta("   [ !! ] Rodando como root/Administrador: rodem como usuário comum."))
    else:
        ok("Executando como usuário comum", "sim (nenhuma estação exige sudo/Administrador)")

    try:
        os.makedirs(LAB, exist_ok=True)
        fd, nome = tempfile.mkstemp(dir=LAB)
        os.close(fd)
        os.remove(nome)
        ok("Pasta de trabalho gravável", LAB)
    except OSError as e:
        atencao("Não foi possível gravar em", "%s (%s)" % (LAB, e))
        return

    alvo = os.path.join(LAB, "alvo_teste.txt")
    open(alvo, "w").close()
    try:
        os.link(alvo, alvo + ".hard")
        ok("Hard links", "suportados")
    except OSError as e:
        atencao("Hard links não funcionam aqui", descrever_erro(e))
    try:
        os.symlink(alvo, alvo + ".sym")
        ok("Links simbólicos", "suportados")
    except OSError as e:
        if WINDOWS:
            print(fraco("   [ -- ] Links simbólicos exigem Administrador ou Modo de Desenvolvedor."))
            print(fraco("          A estação 1 mostra o erro e usa uma junção de diretório no lugar."))
        else:
            atencao("Links simbólicos não funcionam aqui", descrever_erro(e))
    apagar_pasta(LAB)

    ferramentas = {"Linux": ["lsof", "findmnt", "unshare"],
                   "Darwin": ["lsof", "iostat", "hdiutil", "diskutil"],
                   "Windows": ["icacls", "attrib", "whoami", "fsutil"]}.get(SO, [])
    for f in ferramentas:
        if shutil.which(f):
            ok("Ferramenta %s" % f, "encontrada")
        else:
            print(fraco("   [ -- ] Ferramenta %-25s não encontrada (a estação usa outro caminho)" % f))
    if LINUX:
        if os.access("/proc/interrupts", os.R_OK):
            ok("/proc/interrupts", "legível")
        else:
            atencao("/proc/interrupts não está legível")

    print()
    if problemas:
        print(alerta("   Itens a resolver: " + "; ".join(problemas)))
    else:
        print(destaque("   Tudo pronto para a atividade!"))
    print()


if __name__ == "__main__":
    main()
