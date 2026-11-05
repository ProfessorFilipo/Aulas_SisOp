# -*- coding: utf-8 -*-
"""
Estação 5 — Proteção: bits de permissão × ACL
Conceitos: tipos de acesso, dono/grupo/outros (rwx), ACL, permissão do diretório,
EACCES, atributo somente-leitura do Windows.
Silberschatz, 9ª ed.: 11.6 (Protection) e Lista, Questão 5
"""
from comum import *


def tentar(rotulo, funcao):
    try:
        funcao()
        mostrar(rotulo, "PERMITIDO")
    except OSError as e:
        mostrar(rotulo, "NEGADO  -> " + descrever_erro(e))


def ler(p):
    with open(p, "rb") as f:
        f.read()


def escrever(p):
    with open(p, "ab") as f:
        f.write(b"mais uma linha\n")


def modo(p):
    return stat.filemode(os.stat(p).st_mode)


# ------------------------------------------------- ACL do Linux sem setfacl
# O kernel guarda a ACL POSIX no atributo estendido system.posix_acl_access:
# versão (u32 = 2) seguida de entradas (tag u16, permissões u16, id u32).
_TAGS = {0x01: "user", 0x02: "user", 0x04: "group", 0x08: "group", 0x10: "mask", 0x20: "other"}
_SEM_ID = 0xFFFFFFFF


def _perm(n):
    return ("r" if n & 4 else "-") + ("w" if n & 2 else "-") + ("x" if n & 1 else "-")


def acl_linux_definir(arq, uid_extra, perm_extra):
    import struct
    m = os.stat(arq).st_mode
    dono, grupo, outros = (m >> 6) & 7, (m >> 3) & 7, m & 7
    entradas = [(0x01, dono, _SEM_ID), (0x02, perm_extra, uid_extra), (0x04, grupo, _SEM_ID),
                (0x10, grupo | perm_extra, _SEM_ID), (0x20, outros, _SEM_ID)]
    dados = struct.pack("<I", 2) + b"".join(struct.pack("<HHI", *e) for e in entradas)
    os.setxattr(arq, "system.posix_acl_access", dados)


def acl_linux_ler(arq):
    import pwd
    import struct
    try:
        dados = os.getxattr(arq, "system.posix_acl_access")
    except OSError:
        return ["(sem ACL estendida: só os bits rwx)"]
    linhas = []
    for i in range(4, len(dados), 8):
        tag, perm, ident = struct.unpack("<HHI", dados[i:i + 8])
        nome = ""
        if ident != _SEM_ID:
            try:
                nome = pwd.getpwuid(ident).pw_name
            except KeyError:
                nome = str(ident)
        linhas.append("%s:%s:%s" % (_TAGS.get(tag, "?"), nome, _perm(perm)))
    return linhas


# ------------------------------------------------------------------ Unix
def unix(d):
    import grp
    import pwd
    arq = os.path.join(d, "segredo.txt")
    open(arq, "w").write("conteúdo confidencial\n")
    s = os.stat(arq)
    passo("1. Atributos de proteção do arquivo")
    mostrar("Modo:", modo(arq))
    try:
        mostrar("Dono / grupo:", "%s / %s" % (pwd.getpwuid(s.st_uid).pw_name, grp.getgrgid(s.st_gid).gr_name))
    except KeyError:
        mostrar("Dono / grupo (uid/gid):", "%s / %s" % (s.st_uid, s.st_gid))
    if eh_admin():
        print(alerta("   Atenção: vocês estão rodando como root. Rodem sem sudo para ver as negações."))

    passo("2. Tirar do DONO a permissão de leitura")
    prever("Com chmod 200 (só escrita para o dono), o dono ainda consegue ler o arquivo? E escrever?")
    os.chmod(arq, 0o200)
    mostrar("Modo agora:", modo(arq))
    tentar("Ler:", lambda: ler(arq))
    tentar("Escrever:", lambda: escrever(arq))
    prever("Sem poder ler, o dono consegue devolver a permissão a si mesmo (chmod 600)?")
    tentar("chmod 600:", lambda: os.chmod(arq, 0o600))
    mostrar("Modo agora:", modo(arq))
    comando_nativo(linux="chmod u-r segredo.txt ; cat segredo.txt", mac="chmod u-r segredo.txt ; cat segredo.txt")

    passo("3. A permissão do DIRETÓRIO")
    sub = os.path.join(d, "pasta")
    os.mkdir(sub)
    dentro = os.path.join(sub, "dentro.txt")
    open(dentro, "w").write("arquivo dentro da pasta\n")
    os.chmod(dentro, 0o644)
    os.chmod(sub, 0o500)       # r-x: sem escrita na pasta
    mostrar("Modo da pasta / do arquivo:", "%s / %s" % (modo(sub), modo(dentro)))
    prever("A pasta perdeu a permissão de ESCRITA (w), mas o arquivo continua rw para o dono. "
           "Conseguimos (a) alterar o conteúdo do arquivo? (b) apagar o arquivo?")
    tentar("(a) Escrever em pasta/dentro.txt:", lambda: escrever(dentro))
    tentar("(b) Apagar pasta/dentro.txt:", lambda: os.remove(dentro))
    os.chmod(sub, 0o600)       # rw-: sem execução (travessia)
    mostrar("Modo da pasta agora:", modo(sub))
    prever("Agora a pasta tem r e w, mas não tem x (execução). "
           "Conseguimos listar os nomes da pasta? E ler pasta/dentro.txt?")
    tentar("Listar a pasta:", lambda: mostrar("   nomes:", os.listdir(sub)))
    tentar("Ler pasta/dentro.txt:", lambda: ler(dentro))
    os.chmod(sub, 0o700)

    passo("4. Listas de Controle de Acesso (ACL)")
    if MAC:
        usuario = pwd.getpwuid(os.getuid()).pw_name
        prever("Os bits dizem rw para o dono. Uma ACL pode NEGAR leitura ao próprio dono?")
        cod, out = rodar(["chmod", "+a", "%s deny read" % usuario, arq])
        mostrar("chmod +a '%s deny read':" % usuario, "ok" if cod == 0 else out.strip())
        _, out = rodar(["ls", "-le", arq])
        mostrar_saida(out)
        tentar("Ler:", lambda: ler(arq))
        mostrar("Modo (bits) continua:", modo(arq))
        rodar(["chmod", "-N", arq])
        nota("ACL removida com chmod -N.")
    else:
        prever("Com bits rwx, só existem 3 categorias (dono, grupo, outros). Vamos dar leitura a um "
               "usuário ESPECÍFICO (nobody) via ACL. O que muda na saída de ls -l?")
        os.chmod(arq, 0o600)
        _, antes = rodar(["ls", "-l", arq])
        mostrar("ls -l antes:", antes.strip())
        try:
            uid_nobody = pwd.getpwnam("nobody").pw_uid
        except KeyError:
            uid_nobody = 65534
        try:
            if shutil.which("setfacl"):
                cod, out = rodar(["setfacl", "-m", "u:nobody:r", arq])
                if cod != 0:
                    raise OSError(out.strip())
                mostrar("setfacl -m u:nobody:r:", "ok")
            else:
                acl_linux_definir(arq, uid_nobody, 4)
                mostrar("ACL gravada pela chamada de sistema:", "setxattr(system.posix_acl_access)")
            _, depois = rodar(["ls", "-l", arq])
            mostrar("ls -l depois:", depois.strip())
            nota("ACL do arquivo (equivalente ao getfacl):")
            mostrar_saida("\n".join(acl_linux_ler(arq)))
            nota("O 'grupo' exibido por ls -l passa a ser a MÁSCARA da ACL.")
            os.removexattr(arq, "system.posix_acl_access")
        except OSError as e:
            mostrar("Não foi possível gravar a ACL:", str(e))
            nota("O sistema de arquivos desta pasta pode não suportar ACL.")


# --------------------------------------------------------------- Windows
def windows(d):
    arq = os.path.join(d, "segredo.txt")
    open(arq, "w").write("conteúdo confidencial\n")
    passo("1. O que o Python mostra como 'modo' no Windows")
    mostrar("os.stat().st_mode:", modo(arq))
    nota("O NTFS não tem bits rwx. O Python os simula a partir do atributo 'somente leitura'.")

    passo("2. O atributo somente-leitura")
    prever("os.chmod(arquivo, somente leitura) no Windows: ainda conseguimos ler? escrever? apagar?")
    os.chmod(arq, stat.S_IREAD)
    _, out = rodar(["attrib", arq])
    mostrar_saida(out)
    tentar("Ler:", lambda: ler(arq))
    tentar("Escrever:", lambda: escrever(arq))
    tentar("Apagar:", lambda: os.remove(arq))
    os.chmod(arq, stat.S_IREAD | stat.S_IWRITE)

    passo("3. A ACL do arquivo (icacls)")
    _, out = rodar(["icacls", arq])
    mostrar_saida(out)
    nota("(I) = entrada herdada da pasta; F = controle total; M = modificar; R = ler; RX = ler e executar.")
    _, quem = rodar(["whoami"])
    quem = quem.strip()
    prever("Vamos acrescentar uma entrada NEGANDO a leitura de dados (RD) ao próprio usuário %s. "
           "O dono do arquivo ainda consegue ler? E escrever?" % quem)
    cod, out = rodar(["icacls", arq, "/deny", "%s:(RD)" % quem])
    mostrar("icacls /deny:", "ok" if cod == 0 else out.strip())
    _, out = rodar(["icacls", arq])
    mostrar_saida(out)
    tentar("Ler:", lambda: ler(arq))
    tentar("Escrever:", lambda: escrever(arq))
    rodar(["icacls", arq, "/remove:d", quem])
    tentar("Ler (após remover a negação):", lambda: ler(arq))


def main():
    estacao(5, "Proteção: bits de permissão × ACL", "11.6")
    d = pasta("e5")
    if WINDOWS:
        windows(d)
    else:
        unix(d)
    discutir("Bits rwx × ACL: compare granularidade, espaço de metadados e custo de verificação (Questão 5).",
             "No Unix, apagar um arquivo depende da permissão de quem: do arquivo ou do diretório? Por quê?",
             "Por que uma regra DENY costuma ter precedência sobre uma regra ALLOW?",
             "Por que é perigoso trabalhar o tempo todo como root/Administrador?")
    fim("e6_interrupcoes.py")


if __name__ == "__main__":
    main()
