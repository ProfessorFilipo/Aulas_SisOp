# -*- coding: utf-8 -*-
"""
comum.py - funcoes compartilhadas pelas estacoes da atividade pratica
Sistemas Operacionais - PUCRS - Prof. Filipo Novo Mor - filipomor.com

Somente biblioteca padrao do Python (3.8 ou superior).
Funciona em Linux, macOS e Windows.
"""
import datetime
import os
import platform
import shutil
import stat
import subprocess
import sys

SO = platform.system()            # 'Linux', 'Darwin' ou 'Windows'
LINUX = SO == "Linux"
MAC = SO == "Darwin"
WINDOWS = SO == "Windows"
NOME_SO = {"Linux": "Linux", "Darwin": "macOS", "Windows": "Windows"}.get(SO, SO)

SEM_PAUSA = "--sem-pausa" in sys.argv
AQUI = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.join(AQUI, "_lab")
REGISTRO = os.path.join(LAB, "registro_da_dupla.md")
O_BINARY = getattr(os, "O_BINARY", 0)   # so existe no Windows

if WINDOWS:
    os.system("")   # liga as cores ANSI no console do Windows 10/11
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ----------------------------------------------------------------- saida
def _cor(codigo, texto):
    if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
        return texto
    return "\033[%sm%s\033[0m" % (codigo, texto)


def negrito(t):
    return _cor("1", t)


def destaque(t):
    return _cor("1;36", t)


def alerta(t):
    return _cor("1;33", t)


def fraco(t):
    return _cor("2", t)


def registrar(texto):
    """Acrescenta uma linha ao registro da dupla (_lab/registro_da_dupla.md)."""
    try:
        os.makedirs(LAB, exist_ok=True)
        with open(REGISTRO, "a", encoding="utf-8") as f:
            f.write(texto + "\n")
    except OSError:
        pass


def estacao(numero, titulo, secoes):
    linha = "=" * 68
    print()
    print(destaque(linha))
    print(destaque("  ESTAÇÃO %s  |  %s" % (numero, titulo.upper())))
    print(fraco("  Silberschatz, 9ª ed.: %s   |   Sistema: %s (%s)"
                % (secoes, NOME_SO, platform.release())))
    print(destaque(linha))
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    registrar("\n## Estação %s — %s\n\n_%s · %s %s_\n"
              % (numero, titulo, agora, NOME_SO, platform.release()))


def passo(texto):
    print()
    print(negrito(">> " + texto))
    registrar("\n### " + texto + "\n")


def mostrar(rotulo, valor=""):
    print("   %-34s %s" % (rotulo, valor))
    registrar("- %s %s" % (rotulo, valor))


def nota(texto):
    for linha in texto.strip("\n").split("\n"):
        print(fraco("   " + linha))


def prever(pergunta):
    """Mostra a pergunta e espera a previsao da dupla ANTES de executar."""
    print()
    print(alerta("   ? PREVEJAM: ") + pergunta)
    registrar("\n**Previsão pedida:** " + pergunta)
    if SEM_PAUSA:
        return ""
    try:
        resposta = input(alerta("   Previsão da dupla > "))
    except EOFError:
        resposta = ""
    registrar("**Nossa previsão:** " + (resposta or "(em branco)"))
    print(fraco("   ... executando ..."))
    return resposta


def discutir(*perguntas):
    print()
    print(destaque("   PARA DISCUTIR NA DUPLA"))
    registrar("\n**Para discutir:**")
    for p in perguntas:
        print("   - " + p)
        registrar("- " + p)


def comando_nativo(linux=None, mac=None, windows=None):
    """Mostra o comando do proprio SO que revela a mesma informacao."""
    cmd = {"Linux": linux, "Darwin": mac, "Windows": windows}.get(SO)
    if cmd:
        print(fraco("   No terminal do %s:  %s" % (NOME_SO, cmd)))


def descrever_erro(exc):
    """Texto curto com o nome simbolico do erro (nunca so o numero)."""
    import errno as _errno
    partes = [type(exc).__name__]
    if getattr(exc, "errno", None) is not None:
        partes.append("errno %s (%s)" % (exc.errno, _errno.errorcode.get(exc.errno, "?")))
    if getattr(exc, "winerror", None) is not None:
        partes.append("WinError %s" % exc.winerror)
    msg = getattr(exc, "strerror", None) or str(exc)
    return "%s - %s" % (", ".join(partes), msg)


def rodar(cmd, timeout=60, entrada=None):
    """Executa um comando externo e devolve (codigo, saida). Nunca levanta excecao."""
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           input=entrada, timeout=timeout, shell=isinstance(cmd, str))
    except FileNotFoundError:
        return 127, "(comando não encontrado)"
    except subprocess.TimeoutExpired:
        return 124, "(tempo esgotado)"
    except OSError as e:
        return 126, str(e)
    dados = r.stdout or b""
    for cod in (("oem", "utf-8") if WINDOWS else ("utf-8",)):
        try:
            return r.returncode, dados.decode(cod)
        except (UnicodeDecodeError, LookupError):
            continue
    return r.returncode, dados.decode("utf-8", errors="replace")


def mostrar_saida(texto, max_linhas=15, prefixo="   | "):
    linhas = [l for l in texto.rstrip().split("\n")]
    for l in linhas[:max_linhas]:
        print(fraco(prefixo + l.rstrip()))
        registrar("    " + l.rstrip())
    if len(linhas) > max_linhas:
        print(fraco(prefixo + "... (%d linhas omitidas)" % (len(linhas) - max_linhas)))


# --------------------------------------------------------- pasta de trabalho
def _liberar(caminho):
    """Devolve permissoes para que a pasta possa ser apagada."""
    if WINDOWS:
        rodar(["icacls", caminho, "/reset", "/T", "/C", "/Q"], timeout=60)
        rodar(["attrib", "-R", os.path.join(caminho, "*"), "/S", "/D"], timeout=60)
        return
    for raiz, dirs, arqs in os.walk(caminho):
        for nome in dirs + arqs:
            p = os.path.join(raiz, nome)
            try:
                if not os.path.islink(p):
                    os.chmod(p, 0o700)
            except OSError:
                pass
    if MAC:
        rodar(["chmod", "-R", "-N", caminho])


def _ao_falhar(func, caminho, _info):
    try:
        os.chmod(caminho, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
        func(caminho)
    except OSError:
        pass


def apagar_pasta(caminho):
    if os.path.lexists(caminho):
        _liberar(caminho)
        shutil.rmtree(caminho, onerror=_ao_falhar)


def pasta(nome):
    """Cria (do zero) a pasta _lab/<nome> e devolve o caminho absoluto."""
    p = os.path.join(LAB, nome)
    apagar_pasta(p)
    os.makedirs(p)
    return p


def eh_admin():
    if WINDOWS:
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    return hasattr(os, "geteuid") and os.geteuid() == 0


def devolver_ao_usuario():
    """Se rodou com sudo, devolve a posse de _lab ao usuário que chamou o sudo."""
    uid, gid = os.environ.get("SUDO_UID"), os.environ.get("SUDO_GID")
    if WINDOWS or not eh_admin() or not uid or not os.path.isdir(LAB):
        return
    for raiz, dirs, arqs in os.walk(LAB):
        for nome in [raiz] + [os.path.join(raiz, x) for x in dirs + arqs]:
            try:
                os.lchown(nome, int(uid), int(gid or uid))
            except OSError:
                pass


def fim(proxima=None):
    devolver_ao_usuario()
    print()
    print(fraco("   Registro salvo em: %s" % REGISTRO))
    if proxima:
        print(fraco("   Próxima estação: %s" % proxima))
    print()
