# -*- coding: utf-8 -*-
"""
coletar_ambiente.py - registra o ambiente de testes em JSON (Linux, macOS e Windows)
Sistemas Operacionais - PUCRS - Prof. Filipo Novo Mor

Uso:
  python3 coletar_ambiente.py --sistema S1 --saida ../entrega/ambiente --caminhos /pasta/teste /media/pendrive/teste
  (no Windows: py coletar_ambiente.py --sistema S1 --saida ..\\entrega\\ambiente --caminhos C:\\tp D:\\tp)

Somente biblioteca padrao. Rode sem sudo/Administrador.
"""
import argparse
import datetime
import json
import os
import platform
import shutil
import subprocess
import sys

SO = platform.system()


def rodar(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        return r.stdout.decode("utf-8", "replace").strip()
    except Exception as e:  # noqa: BLE001
        return "(indisponivel: %s)" % e


def ler(caminho):
    try:
        with open(caminho, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def cpu_e_memoria():
    info = {"nucleos_logicos": os.cpu_count()}
    if SO == "Linux":
        for l in ler("/proc/cpuinfo").splitlines():
            if l.startswith("model name"):
                info["cpu"] = l.split(":", 1)[1].strip()
                break
        for l in ler("/proc/meminfo").splitlines():
            if l.startswith("MemTotal"):
                info["ram_bytes"] = int(l.split()[1]) * 1024
    elif SO == "Darwin":
        info["cpu"] = rodar(["sysctl", "-n", "machdep.cpu.brand_string"])
        try:
            info["ram_bytes"] = int(rodar(["sysctl", "-n", "hw.memsize"]))
        except ValueError:
            pass
    elif SO == "Windows":
        info["cpu"] = platform.processor()
        try:
            import ctypes

            class MEM(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = MEM()
            m.dwLength = ctypes.sizeof(MEM)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            info["ram_bytes"] = m.ullTotalPhys
        except Exception:  # noqa: BLE001
            pass
    return info


def sistema_de_arquivos(caminho):
    real = os.path.realpath(caminho)
    d = {"caminho": caminho, "existe": os.path.exists(real)}
    if not d["existe"]:
        return d
    st = os.stat(real)
    d["st_dev"] = st.st_dev
    d["st_blksize"] = getattr(st, "st_blksize", None)
    uso = shutil.disk_usage(real)
    d["livre_bytes"], d["total_bytes"] = uso.free, uso.total
    if SO == "Windows":
        import ctypes
        k = ctypes.windll.kernel32
        raiz = ctypes.create_unicode_buffer(300)
        k.GetVolumePathNameW(ctypes.c_wchar_p(real), raiz, 300)
        nome = ctypes.create_unicode_buffer(64)
        k.GetVolumeInformationW(ctypes.c_wchar_p(raiz.value), None, 0, None, None, None, nome, 64)
        spc, bps, a, b = (ctypes.c_ulong() for _ in range(4))
        k.GetDiskFreeSpaceW(ctypes.c_wchar_p(raiz.value), ctypes.byref(spc), ctypes.byref(bps), ctypes.byref(a), ctypes.byref(b))
        d.update({"ponto_de_montagem": raiz.value, "tipo": nome.value, "cluster_bytes": spc.value * bps.value})
        return d
    vfs = os.statvfs(real)
    d["bloco_bytes"] = vfs.f_frsize
    if SO == "Linux":
        melhor = ("", "", "", "")
        for linha in ler("/proc/self/mountinfo").splitlines():
            esq, _, dir_ = linha.partition(" - ")
            ponto = esq.split()[4].encode().decode("unicode_escape")
            tipo, origem, opcoes = (dir_.split() + ["", "", ""])[:3]
            if (real == ponto or real.startswith(ponto.rstrip("/") + "/")) and len(ponto) >= len(melhor[0]):
                melhor = (ponto, tipo, origem, opcoes)
        d.update(dict(zip(["ponto_de_montagem", "tipo", "origem", "opcoes"], melhor)))
    else:
        melhor = ("", "", "")
        for linha in rodar(["mount"]).splitlines():
            origem, _, resto = linha.partition(" on ")
            ponto, _, opcoes = resto.rpartition(" (")
            if (real == ponto or real.startswith(ponto.rstrip("/") + "/")) and len(ponto) >= len(melhor[0]):
                melhor = (ponto, origem, opcoes.rstrip(")"))
        d.update({"ponto_de_montagem": melhor[0], "origem": melhor[1], "opcoes": melhor[2],
                  "tipo": melhor[2].split(",")[0]})
    return d


def discos():
    if SO == "Linux":
        return rodar(["lsblk", "-o", "NAME,SIZE,ROTA,TRAN,MODEL,FSTYPE,MOUNTPOINT"])
    if SO == "Darwin":
        return rodar(["diskutil", "list"])
    if SO == "Windows":
        return rodar(["powershell", "-NoProfile", "-Command",
                      "Get-PhysicalDisk | Select FriendlyName,MediaType,BusType,Size | Format-Table -AutoSize | Out-String -Width 200"])
    return ""


def virtualizacao():
    if SO == "Linux":
        if shutil.which("systemd-detect-virt"):
            return rodar(["systemd-detect-virt"])
        return "wsl" if "microsoft" in platform.release().lower() else "desconhecido"
    if SO == "Darwin":
        return "vm" if rodar(["sysctl", "-n", "kern.hv_vmm_present"]) == "1" else "none"
    return rodar(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_ComputerSystem).Model"])


def main():
    ap = argparse.ArgumentParser(description="Registra o ambiente de testes do trabalho.")
    ap.add_argument("--sistema", required=True, help="ID do sistema em grupo.json (S1, S2...)")
    ap.add_argument("--saida", default=".", help="pasta onde gravar ambiente_<ID>.json")
    ap.add_argument("--caminhos", nargs="*", default=[], help="pastas de teste (uma por sistema de arquivos)")
    a = ap.parse_args()

    dados = {
        "sistema_id": a.sistema,
        "coletado_em": datetime.datetime.now().isoformat(timespec="seconds"),
        "so": SO, "so_release": platform.release(), "so_versao": platform.version(),
        "mac_versao": platform.mac_ver()[0] if SO == "Darwin" else None,
        "arquitetura": platform.machine(), "python": platform.python_version(),
        "executavel_python": sys.executable,
        "virtualizacao": virtualizacao(),
        "hardware": cpu_e_memoria(),
        "sistemas_de_arquivos": [sistema_de_arquivos(c) for c in a.caminhos],
        "discos": discos(),
    }
    if SO == "Linux":
        dados["linux"] = {
            "dirty_expire_centisecs": ler("/proc/sys/vm/dirty_expire_centisecs").strip(),
            "dirty_ratio": ler("/proc/sys/vm/dirty_ratio").strip(),
            "ulimit_n": rodar(["sh", "-c", "ulimit -n"]),
            "escalonadores_de_es": {d: ler("/sys/block/%s/queue/scheduler" % d).strip()
                                    for d in sorted(os.listdir("/sys/block")) if not d.startswith(("loop", "ram"))}
            if os.path.isdir("/sys/block") else {},
        }
    elif SO == "Darwin":
        dados["macos"] = {"ulimit_n": rodar(["sh", "-c", "ulimit -n"]),
                          "maxfilesperproc": rodar(["sysctl", "-n", "kern.maxfilesperproc"])}
    os.makedirs(a.saida, exist_ok=True)
    destino = os.path.join(a.saida, "ambiente_%s.json" % a.sistema)
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print("Ambiente registrado em", destino)


if __name__ == "__main__":
    main()
