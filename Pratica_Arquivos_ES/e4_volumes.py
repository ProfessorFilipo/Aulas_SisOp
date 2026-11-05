# -*- coding: utf-8 -*-
"""
Estação 4 — Volumes, montagem e os limites de um sistema de arquivos
Conceitos: volume/partição, ponto de montagem, tipo de sistema de arquivos,
tamanho de bloco/cluster, links e renomeação entre volumes (EXDEV).
Silberschatz, 9ª ed.: 11.3.1 (Storage Structure), 11.4 (File-System Mounting)

Nada aqui exige sudo ou Administrador:
  - macOS: se não houver um segundo volume gravável, o script cria um com uma imagem de disco;
  - Linux: a montagem do passo 5 é feita em um namespace próprio (unshare), sem sudo.
"""
import glob
import re
import tempfile

from comum import *


# -------------------------------------------------- tipo de sistema de arquivos
def _montagens_linux():
    tab = []
    with open("/proc/self/mountinfo") as f:
        for linha in f:
            esq, _, dir_ = linha.partition(" - ")
            campos = esq.split()
            ponto = campos[4].encode().decode("unicode_escape")
            tipo, origem = dir_.split()[:2]
            tab.append((ponto, tipo, origem))
    return tab


def _montagens_mac():
    tab = []
    _, out = rodar(["mount"])
    for linha in out.splitlines():
        if " on " not in linha or " (" not in linha:
            continue
        origem, _, resto = linha.partition(" on ")
        ponto, _, opcoes = resto.rpartition(" (")
        tab.append((ponto, opcoes.split(",")[0].strip(" )"), origem))
    return tab


def info_windows(caminho):
    import ctypes
    k = ctypes.windll.kernel32
    raiz = ctypes.create_unicode_buffer(300)
    k.GetVolumePathNameW(ctypes.c_wchar_p(caminho), raiz, 300)
    nome_fs = ctypes.create_unicode_buffer(64)
    if not k.GetVolumeInformationW(ctypes.c_wchar_p(raiz.value), None, 0, None, None, None, nome_fs, 64):
        return raiz.value, "?", "?"
    spc, bps, livres, total = (ctypes.c_ulong() for _ in range(4))
    cluster = "?"
    if k.GetDiskFreeSpaceW(ctypes.c_wchar_p(raiz.value), ctypes.byref(spc), ctypes.byref(bps),
                           ctypes.byref(livres), ctypes.byref(total)):
        cluster = spc.value * bps.value
    return raiz.value, nome_fs.value, cluster


def _montagem_mac(real):
    """No macOS, o df resolve os firmlinks (ex.: /Users fica no volume de dados)."""
    cod, out = rodar(["df", "-P", real])
    linhas = [l for l in out.splitlines() if l.strip()]
    if cod != 0 or len(linhas) < 2:
        return None
    partes = linhas[-1].split()
    origem, ponto = partes[0], " ".join(partes[5:])
    tipo = "?"
    for p_, t, o in _montagens_mac():
        if o == origem or p_ == ponto:
            tipo = t
            break
    return ponto, tipo, origem


def descrever(caminho):
    """Devolve (ponto_de_montagem, tipo_fs, origem, bloco)."""
    real = os.path.realpath(caminho)
    if WINDOWS:
        raiz, tipo, cluster = info_windows(real)
        return raiz, tipo, "", cluster
    if MAC:
        r = _montagem_mac(real)
        if r:
            try:
                bloco = os.statvfs(real).f_frsize
            except OSError:
                bloco = "?"
            return r[0], r[1], r[2], bloco
    tab = _montagens_linux() if LINUX else _montagens_mac()
    melhor = ("/", "?", "?")
    for ponto, tipo, origem in tab:
        if (real == ponto or real.startswith(ponto.rstrip("/") + "/")) and len(ponto) >= len(melhor[0]):
            melhor = (ponto, tipo, origem)
    try:
        bloco = os.statvfs(real).f_frsize
    except OSError:
        bloco = "?"
    return melhor[0], melhor[1], melhor[2], bloco


# -------------------------------------------------------------- candidatos
def candidatos():
    lista = [AQUI, os.path.expanduser("~"), tempfile.gettempdir()]
    if WINDOWS:
        import string
        import ctypes
        mascara = ctypes.windll.kernel32.GetLogicalDrives()
        lista += ["%s:\\" % l for i, l in enumerate(string.ascii_uppercase) if mascara >> i & 1]
    else:
        lista += ["/"]
        if LINUX:
            lista += ["/dev/shm", "/run/user/%d" % os.getuid(), "/proc", "/sys", "/boot/efi", "/media"]
            lista += glob.glob("/media/*/*") + glob.glob("/run/media/*/*")
        if MAC:
            lista += ["/System/Volumes/Data", "/dev"] + glob.glob("/Volumes/*")
    vistos, saida = set(), []
    for p in lista:
        if os.path.isdir(p) and os.path.realpath(p) not in vistos:
            vistos.add(os.path.realpath(p))
            saida.append(p)
    return saida


def gravavel(p):
    try:
        fd, nome = tempfile.mkstemp(dir=p, prefix=".sisop_")
        os.close(fd)
        os.remove(nome)
        return True
    except OSError:
        return False


# ------------------------------------------------------------------ extras
def _anexar_imagem_mac(nome, extra=()):
    """Cria uma imagem de disco HFS+ de 16 MiB dentro de _lab e a anexa. Não exige administrador."""
    os.makedirs(LAB, exist_ok=True)
    img = os.path.join(LAB, nome + ".dmg")
    cod, out = rodar(["hdiutil", "create", "-ov", "-size", "16m", "-fs", "HFS+", "-volname", nome, img], timeout=120)
    if cod != 0:
        mostrar("hdiutil create falhou:", out.strip()[-300:])
        return None
    cod, out = rodar(["hdiutil", "attach", "-nobrowse"] + list(extra) + [img], timeout=120)
    m = re.search(r"\t(/[^\t\n]+)\s*$", out, re.M)
    if cod != 0 or not m:
        mostrar("hdiutil attach falhou:", out.strip()[-300:])
        return None
    ponto = m.group(1).strip()
    with open(os.path.join(LAB, "volumes_mac.txt"), "a") as f:
        f.write(ponto + "\n")            # anotado para o 99_limpar desanexar
    return ponto


def criar_volume_mac():
    existentes = glob.glob("/Volumes/LAB_SISOP*")
    for v in existentes:
        if os.path.ismount(v) and gravavel(v):
            return v
    v = _anexar_imagem_mac("LAB_SISOP")
    if v:
        mostrar("Segundo volume criado (imagem de disco):", v)
    return v


def _montar_linux(ponto):
    """Monta um tmpfs em um namespace de montagem próprio (unshare): não exige sudo."""
    roteiro = ('mount -t tmpfs -o size=8m tmpfs "$1" || exit 3; echo "== montado"; ls -1 "$1"; '
               'echo criado > "$1/c_novo.txt"; echo "== criado"; ls -1 "$1"; '
               'umount "$1"; echo "== desmontado"; ls -1 "$1"')
    if not shutil.which("unshare"):
        mostrar("Comando unshare não encontrado.", "")
        return None
    cod, out = rodar(["unshare", "--user", "--map-root-user", "--mount", "sh", "-c", roteiro, "sh", ponto])
    if cod != 0 or "== montado" not in out:
        mostrar("A montagem foi recusada:", out.strip().splitlines()[-1] if out.strip() else "código %d" % cod)
        nota("Este sistema não deixa um usuário comum montar sistemas de arquivos, nem em um\n"
             "namespace próprio (o Ubuntu 24.04, por exemplo, restringe isso com o AppArmor).\n"
             "Discutam: por que montar exige privilégio? O que um usuário mal-intencionado poderia\n"
             "esconder montando algo sobre /etc ou sobre a pasta de outro usuário?")
        return None
    etapas, atual = {}, None
    for linha in out.splitlines():
        if linha.startswith("== "):
            atual = linha[3:].strip()
            etapas[atual] = []
        elif atual:
            etapas[atual].append(linha.strip())
    nota("(montagem feita em um namespace de montagem privado, criado com unshare)")
    return etapas


def _montar_mac(ponto):
    etapas = {}
    v = _anexar_imagem_mac("MONTAGEM", extra=["-mountpoint", ponto])
    if not v:
        nota("O macOS recusou a montagem nesta pasta. Discutam a Questão 7 a partir da teoria.")
        return None
    etapas["montado"] = sorted(x for x in os.listdir(ponto) if not x.startswith("."))
    open(os.path.join(ponto, "c_novo.txt"), "w").write("criado no volume montado\n")
    etapas["criado"] = sorted(x for x in os.listdir(ponto) if not x.startswith("."))
    rodar(["hdiutil", "detach", ponto])
    etapas["desmontado"] = sorted(x for x in os.listdir(ponto) if not x.startswith("."))
    return etapas


def montar_sobre_pasta(d):
    ponto = os.path.join(d, "ponto")
    os.makedirs(ponto)
    for nome in ("a_antes.txt", "b_antes.txt"):
        open(os.path.join(ponto, nome), "w").write("existia antes da montagem\n")
    mostrar("Conteúdo de ponto/ ANTES de montar:", sorted(os.listdir(ponto)))
    prever("Vamos montar um sistema de arquivos vazio em ponto/ e criar nele c_novo.txt. "
           "Durante a montagem, o que acontece com a_antes.txt e b_antes.txt? "
           "E depois de desmontar, o que aparece em ponto/?")
    etapas = _montar_linux(ponto) if LINUX else _montar_mac(ponto)
    if not etapas:
        return
    mostrar("DURANTE a montagem:", etapas.get("montado"))
    mostrar("Depois de criar c_novo.txt:", etapas.get("criado"))
    mostrar("DEPOIS de desmontar:", etapas.get("desmontado"))


def main():
    estacao(4, "Volumes, montagem e limites", "11.3.1 e 11.4")
    d = pasta("e4")

    passo("1. Em que volume está cada pasta?")
    prever("Vocês acham que a pasta pessoal, a pasta temporária e a raiz estão no mesmo volume? "
           "Que tipo de sistema de arquivos esperam encontrar?")
    print("   %-28s %-12s %-10s %-9s %s" % ("pasta", "volume", "tipo", "bloco", "montado em"))
    lista = candidatos()
    for p in lista:
        try:
            dev = os.stat(p).st_dev
            ponto, tipo, origem, bloco = descrever(p)
        except OSError as e:
            print("   %-28s %s" % (p[-28:], descrever_erro(e)))
            continue
        rotulo = {AQUI: "(pasta da atividade)", os.path.expanduser("~"): "~ (pasta pessoal)",
                  tempfile.gettempdir(): "(pasta temporária)"}.get(p, p)
        print("   %-28s %-12s %-10s %-9s %s %s" % (rotulo[-28:], dev, tipo, bloco, ponto, fraco(origem)))
        registrar("- %s: volume=%s tipo=%s bloco=%s montado_em=%s origem=%s" % (p, dev, tipo, bloco, ponto, origem))
    nota("volume = st_dev, o número que identifica o dispositivo/sistema de arquivos.\n"
         "bloco = unidade de alocação (bloco no Linux/macOS, cluster no Windows).")
    comando_nativo(linux="findmnt   ou   df -Th", mac="mount ; df -h ; diskutil list",
                   windows="fsutil fsinfo volumeinfo C:   ou   Get-Volume (PowerShell)")

    passo("2. Procurando um SEGUNDO volume onde se possa gravar")
    dev_aqui = os.stat(d).st_dev
    outro = None
    for p in lista:
        try:
            if os.stat(p).st_dev != dev_aqui and gravavel(p):
                outro = p
                break
        except OSError:
            continue
    if not outro and MAC:
        nota("Nenhum outro volume gravável: vamos criar um, com uma imagem de disco (sem administrador).")
        outro = criar_volume_mac()
    if not outro:
        mostrar("Nenhum outro volume gravável encontrado.", "")
        nota("Windows: conectem um pendrive e rodem a estação de novo, ou façam esta parte\n"
             "com uma dupla vizinha que use Linux ou macOS.")
    else:
        mostrar("Volume desta pasta:", dev_aqui)
        mostrar("Outro volume encontrado:", "%s (volume %s)" % (outro, os.stat(outro).st_dev))
        origem = os.path.join(d, "viajante.txt")
        open(origem, "w").write("vou tentar mudar de volume\n")
        destino_dir = tempfile.mkdtemp(dir=outro, prefix="sisop_e4_")

        passo("3. Hard link entre volumes")
        prever("Um hard link para viajante.txt dentro de %s: funciona?" % outro)
        try:
            os.link(origem, os.path.join(destino_dir, "rigido.txt"))
            mostrar("os.link():", "funcionou")
        except OSError as e:
            mostrar("os.link() falhou:", descrever_erro(e))

        passo("4. Mover (renomear) para outro volume")
        prever("os.rename() de viajante.txt para o outro volume é instantâneo como dentro do "
               "mesmo volume? E o comando 'mover' do sistema (shutil.move)?")
        alvo = os.path.join(destino_dir, "viajante.txt")
        try:
            os.rename(origem, alvo)
            mostrar("os.rename():", "funcionou")
        except OSError as e:
            mostrar("os.rename() falhou:", descrever_erro(e))
            id_antes = os.stat(origem).st_ino
            shutil.move(origem, alvo)
            mostrar("shutil.move():", "funcionou")
            mostrar("ID antes e depois de mover:", "%s -> %s" % (id_antes, os.stat(alvo).st_ino))
        apagar_pasta(destino_dir)

    passo("5. Montar sobre uma pasta que já tem arquivos (Lista, Questão 7)")
    if WINDOWS:
        nota("No Windows, um volume só pode ser montado em uma pasta NTFS VAZIA, e isso exige\n"
             "Administrador. Comparem com a dupla vizinha que use Linux ou macOS.")
    else:
        montar_sobre_pasta(d)

    discutir("Por que mover um arquivo de 5 GB entre pastas do mesmo disco é instantâneo, "
             "mas para um pendrive demora?",
             "Por que o hard link não cruza volumes, e o link simbólico cruza?",
             "No Windows, um volume só pode ser montado em uma pasta NTFS VAZIA. "
             "No Unix, a pasta pode ter arquivos. O que acontece com eles? (Questão 7)")
    fim("e5_protecao.py")


if __name__ == "__main__":
    main()
