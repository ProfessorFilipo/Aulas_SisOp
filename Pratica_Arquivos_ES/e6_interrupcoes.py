# -*- coding: utf-8 -*-
"""
Estação 6 — Interrupções e DMA: contando o que o hardware faz
Conceitos: interrupção, vetor/linhas de IRQ, MSI, temporizador, DMA (muitos bytes por
interrupção), segunda metade do tratador (softirq no Linux, DPC no Windows).
Silberschatz, 9ª ed.: 13.2.2 (Interrupts), 13.2.3 (DMA), 13.5 (ciclo de vida de um read())

Três fases de alguns segundos: PARADO, DIGITANDO/MEXENDO O MOUSE, GRAVANDO NO DISCO
(e, no Linux e no macOS, LENDO DO DISCO sem cache).
Nada exige sudo/Administrador. No macOS, sem administrador, o disco é observado pelo iostat.
"""
import re
import tempfile
import time

from comum import *

DURACAO = 5
DISCO_RE = re.compile(r"nvme|ahci|ata|mmc|sdhci|virtio|xhci|ehci|usb-storage", re.I)


# ================================================================ Linux
def _tabela_proc(caminho):
    with open(caminho) as f:
        linhas = f.read().splitlines()
    ncpu = len(linhas[0].split())
    tab = {}
    for l in linhas[1:]:
        partes = l.split()
        if not partes:
            continue
        chave = partes[0].rstrip(":")
        nums = []
        for p in partes[1:1 + ncpu]:
            if not p.isdigit():
                break
            nums.append(int(p))
        nome = " ".join(partes[1 + len(nums):])
        tab[chave] = (sum(nums), nome)
    return tab


def coletar_linux():
    amostra = {"irq": _tabela_proc("/proc/interrupts"), "soft": _tabela_proc("/proc/softirqs")}
    with open("/proc/stat") as f:
        for l in f:
            if l.startswith("intr "):
                amostra["intr"] = int(l.split()[1])
            elif l.startswith("ctxt "):
                amostra["ctxt"] = int(l.split()[1])
    return amostra


def delta_linux(a, b, dt):
    linhas = []
    for k, (v, nome) in b["irq"].items():
        dv = v - a["irq"].get(k, (0, ""))[0]
        if dv > 0:
            linhas.append((dv, k, nome))
    linhas.sort(reverse=True)
    disco = sum(dv for dv, k, nome in linhas if DISCO_RE.search(nome))
    soft = {k: b["soft"][k][0] - a["soft"].get(k, (0, ""))[0] for k in b["soft"]}
    return {"total_s": (b["intr"] - a["intr"]) / dt, "disco": disco, "disco_s": disco / dt,
            "block_s": soft.get("BLOCK", 0) / dt, "ctxt_s": (b["ctxt"] - a["ctxt"]) / dt,
            "top": linhas[:6]}


# ============================================================== Windows
class ContadoresWindows:
    NOMES = [("interrupcoes_s", r"\Processor(_Total)\Interrupts/sec"),
             ("dpcs_s", r"\Processor(_Total)\DPCs Queued/sec"),
             ("transf_disco_s", r"\PhysicalDisk(_Total)\Disk Transfers/sec"),
             ("bytes_por_transf", r"\PhysicalDisk(_Total)\Avg. Disk Bytes/Transfer")]

    def __init__(self):
        import ctypes
        from ctypes import wintypes
        self.ct = ctypes

        class Valor(ctypes.Structure):
            _fields_ = [("CStatus", wintypes.DWORD), ("valor", ctypes.c_double)]
        self.Valor = Valor
        pdh = ctypes.WinDLL("pdh.dll")
        H = wintypes.HANDLE
        pdh.PdhOpenQueryW.argtypes = [wintypes.LPCWSTR, ctypes.c_size_t, ctypes.POINTER(H)]
        pdh.PdhAddEnglishCounterW.argtypes = [H, wintypes.LPCWSTR, ctypes.c_size_t, ctypes.POINTER(H)]
        pdh.PdhCollectQueryData.argtypes = [H]
        pdh.PdhGetFormattedCounterValue.argtypes = [H, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
                                                    ctypes.POINTER(Valor)]
        for fn in (pdh.PdhOpenQueryW, pdh.PdhAddEnglishCounterW, pdh.PdhCollectQueryData,
                   pdh.PdhGetFormattedCounterValue):
            fn.restype = wintypes.LONG
        self.pdh = pdh
        self.q = H()
        if pdh.PdhOpenQueryW(None, 0, ctypes.byref(self.q)) != 0:
            raise OSError("PdhOpenQuery falhou")
        self.c = {}
        for chave, nome in self.NOMES:
            h = H()
            if pdh.PdhAddEnglishCounterW(self.q, nome, 0, ctypes.byref(h)) == 0:
                self.c[chave] = h
        if not self.c:
            raise OSError("nenhum contador disponível")

    def iniciar(self):
        self.pdh.PdhCollectQueryData(self.q)

    def ler(self):
        self.pdh.PdhCollectQueryData(self.q)
        saida = {}
        for chave, h in self.c.items():
            v = self.Valor()
            if self.pdh.PdhGetFormattedCounterValue(h, 0x200, None, self.ct.byref(v)) == 0:
                saida[chave] = v.valor
        return saida


# ================================================================ macOS
def iniciar_mac(dur):
    procs = {"iostat": subprocess.Popen(["iostat", "-d", "-w", "1", "-c", str(dur + 1)],
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)}
    if eh_admin():
        procs["power"] = subprocess.Popen(["powermetrics", "--samplers", "interrupts", "-i",
                                           str(dur * 1000), "-n", "1"],
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return procs


def terminar_mac(procs):
    res = {}
    for k, p in procs.items():
        try:
            out, _ = p.communicate(timeout=DURACAO + 10)
            res[k] = out.decode("utf-8", "replace")
        except subprocess.TimeoutExpired:
            p.kill()
            res[k] = ""
    if "power" in res:
        totais = [float(x) for x in re.findall(r"Total IRQ:\s*([\d.]+)", res["power"])]
        res["irq_s"] = sum(totais) if totais else None
    return res


# ============================================================ cargas
def esperar(dur, digitar=False):
    """Espera 'dur' segundos com contagem regressiva; sem eco de teclas."""
    antigo = None
    if digitar and not WINDOWS and sys.stdin.isatty():
        import termios
        antigo = termios.tcgetattr(sys.stdin)
        novo = termios.tcgetattr(sys.stdin)
        novo[3] &= ~(termios.ECHO | termios.ICANON)
        termios.tcsetattr(sys.stdin, termios.TCSANOW, novo)
    try:
        for s in range(dur, 0, -1):
            print("\r   ... %d s " % s, end="", flush=True)
            time.sleep(1)
        print("\r" + " " * 20 + "\r", end="")
    finally:
        if antigo is not None:
            import termios
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
            termios.tcsetattr(sys.stdin, termios.TCSANOW, antigo)
        elif WINDOWS:
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getwch()


def gravar(caminho, total):
    bloco = os.urandom(1 << 20)
    fd = os.open(caminho, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | O_BINARY)
    if MAC:
        import fcntl
        fcntl.fcntl(fd, getattr(fcntl, "F_NOCACHE", 48), 1)  # não guarda o que gravar no cache
    feitos = 0
    while feitos < total:
        os.write(fd, bloco)
        feitos += len(bloco)
        if feitos % (16 << 20) == 0:
            os.fsync(fd)
    os.fsync(fd)
    os.close(fd)
    return feitos


def ler_sem_cache(caminho):
    fd = os.open(caminho, os.O_RDONLY | O_BINARY)
    if LINUX:
        os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)   # descarta do cache do kernel
    elif MAC:
        import fcntl
        fcntl.fcntl(fd, getattr(fcntl, "F_NOCACHE", 48), 1)  # lê sem passar pelo cache
    feitos = 0
    while True:
        b = os.read(fd, 1 << 20)
        if not b:
            break
        feitos += len(b)
    os.close(fd)
    return feitos


# ============================================================== fases
def executar_fase(nome, instrucao, carga):
    passo(nome)
    print("   " + instrucao)
    if not SEM_PAUSA:
        try:
            input(fraco("   Enter para começar > "))
        except EOFError:
            pass
    medidor = None
    if LINUX:
        antes = coletar_linux()
    elif WINDOWS:
        medidor = ContadoresWindows() if CONT_WIN_OK else None
        if medidor:
            medidor.iniciar()
    elif MAC:
        procs = iniciar_mac(DURACAO)
    t0 = time.perf_counter()
    nbytes = carga()
    dt = time.perf_counter() - t0
    r = {"fase": nome, "dt": dt, "bytes": nbytes or 0}
    if LINUX:
        r.update(delta_linux(antes, coletar_linux(), dt))
    elif WINDOWS and medidor:
        r.update(medidor.ler())
    elif MAC:
        r.update(terminar_mac(procs))
    mostrar_fase(r)
    return r


def mostrar_fase(r):
    mostrar("Duração da fase:", "%.2f s" % r["dt"])
    if r["bytes"]:
        mostrar("Bytes transferidos pelo script:", "%.0f MiB" % (r["bytes"] / 2 ** 20))
    if LINUX:
        mostrar("Interrupções por segundo (total):", "%.0f" % r["total_s"])
        mostrar("Interrupções/s das controladoras de disco:", "%.0f" % r["disco_s"])
        mostrar("softirq BLOCK por segundo (2ª metade):", "%.0f" % r["block_s"])
        mostrar("Trocas de contexto por segundo:", "%.0f" % r["ctxt_s"])
        if r["bytes"] and r["disco"]:
            mostrar("Bytes por interrupção de disco:", "%.0f (%.0f KiB)" % (r["bytes"] / r["disco"],
                                                                            r["bytes"] / r["disco"] / 1024))
        nota("Linhas de IRQ que mais cresceram nesta fase:")
        for dv, k, nome in r["top"]:
            print(fraco("     %8d  %-5s %s" % (dv, k, nome[-60:])))
            registrar("    %8d  %-5s %s" % (dv, k, nome))
    elif WINDOWS:
        if not CONT_WIN_OK:
            return
        for chave, rot in (("interrupcoes_s", "Interrupções por segundo:"),
                           ("dpcs_s", "DPCs por segundo (2ª metade):"),
                           ("transf_disco_s", "Transferências de disco por segundo:"),
                           ("bytes_por_transf", "Bytes por transferência de disco:")):
            if chave in r:
                mostrar(rot, "%.0f" % r[chave])
    elif MAC:
        if r.get("irq_s") is not None:
            mostrar("Interrupções por segundo (soma das CPUs):", "%.0f" % r["irq_s"])
        elif "power" in r:
            linhas = [l for l in r["power"].splitlines() if re.search(r"IRQ|interrupt|TIMER|IPI", l, re.I)]
            mostrar_saida("\n".join(linhas) or r["power"], 12)
        linhas = r.get("iostat", "").splitlines()
        if len(linhas) > 3:
            del linhas[2]          # 1ª linha de dados = média desde o boot: não é desta fase
        nota("iostat, uma linha por segundo (KB/t = KiB por transferência; tps = transferências/s):")
        mostrar_saida("\n".join(linhas), 10)


CONT_WIN_OK = False


def main():
    global CONT_WIN_OK
    estacao(6, "Interrupções e DMA", "13.2.2, 13.2.3 e 13.5")
    if WINDOWS:
        try:
            ContadoresWindows()
            CONT_WIN_OK = True
        except Exception as e:
            mostrar("Contadores de desempenho indisponíveis:", str(e))
            nota("Alternativa: abram o Monitor de Desempenho (perfmon) e adicionem\n"
                 "Processador > Interrupções/s e Disco Físico > Média de bytes/transferência.")
    if MAC and not eh_admin():
        print(alerta("   macOS: sem administrador, o sistema não expõe a contagem de interrupções."))
        print(fraco("   Vamos observar o disco pelo iostat (KiB por transferência), que também evidencia o DMA."))
        print(fraco("   Se a conta for de administrador, dá para ver as interrupções com: sudo python3 e6_interrupcoes.py"))
    comando_nativo(linux="watch -n1 -d cat /proc/interrupts",
                   mac="sudo powermetrics --samplers interrupts -i 1000 -n 1",
                   windows="Gerenciador de Dispositivos > Exibir > Recursos por tipo  (veja as IRQs)")

    d = pasta("e6")
    livre = shutil.disk_usage(d).free
    tamanho = (256 << 20) if livre > (2 << 30) else (64 << 20)
    arq = os.path.join(d, "carga.bin")

    prever("Em qual fase haverá MAIS interrupções por segundo: parado, digitando ou gravando no disco? "
           "E ao gravar %d MiB, quantos bytes vocês esperam por interrupção do disco: "
           "1 byte, 512 bytes ou dezenas de KiB?" % (tamanho >> 20))

    resultados = [executar_fase("Fase 1: PARADO", "Não toquem no teclado nem no mouse por %d s." % DURACAO,
                                lambda: esperar(DURACAO)),
                  executar_fase("Fase 2: DIGITANDO", "Digitem sem parar e mexam o mouse/touchpad por %d s."
                                % DURACAO, lambda: esperar(DURACAO, digitar=True)),
                  executar_fase("Fase 3: GRAVANDO NO DISCO", "Não toquem em nada. Gravando %d MiB com fsync."
                                % (tamanho >> 20), lambda: gravar(arq, tamanho))]
    if LINUX or MAC:
        resultados.append(executar_fase("Fase 4: LENDO DO DISCO (sem cache)",
                                        "Não toquem em nada. Lendo o arquivo de volta.",
                                        lambda: ler_sem_cache(arq)))
    try:
        os.remove(arq)
    except OSError:
        pass

    if LINUX:
        passo("Resumo")
        print("   %-36s %10s %10s %10s" % ("fase", "irq/s", "disco/s", "B/irq disco"))
        for r in resultados:
            bpi = "%.0f" % (r["bytes"] / r["disco"]) if r["bytes"] and r["disco"] else "-"
            print("   %-36s %10.0f %10.0f %10s" % (r["fase"], r["total_s"], r["disco_s"], bpi))

    discutir("A fase PARADO não teve zero interrupções. Quem gerou essas interrupções?",
             "Por que gravar centenas de MiB gera relativamente POUCAS interrupções de disco? "
             "O que isso diz sobre o DMA?",
             "Se cada byte do disco gerasse uma interrupção (E/S programada), quanto tempo de CPU "
             "isso custaria?",
             "softirq (Linux) e DPC (Windows) são a 'segunda metade' do tratador. "
             "Por que dividir o tratamento em duas partes? (exercício 13.14)")
    fim("extra_bloqueio.py (desafio) ou 99_limpar.py")


if __name__ == "__main__":
    main()
