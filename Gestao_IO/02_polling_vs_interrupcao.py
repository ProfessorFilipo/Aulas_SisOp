#!/usr/bin/env python3
"""Tópico 13.2.1 e 13.2.2 — Polling × interrupções.

Um "dispositivo" (uma thread) fica pronto depois de alguns segundos.
  * Polling: a CPU consulta o "registrador de status" sem parar (espera ocupada).
  * Interrupção: o processo dorme e é acordado quando o dispositivo fica pronto.
Compare o tempo de CPU gasto em cada estratégia.

Gestão de Entrada e Saída — Sistemas Operacionais (PUCRS)
Prof. Filipo Novo Mór - filipomor.com - github.com/ProfessorFilipo
"""
import os
import threading
import time

from comum import LINUX, MAC, titulo, nota

ESPERA = 3.0  # segundos até o "dispositivo" ficar pronto


def dispositivo(fd_escrita):
    time.sleep(ESPERA)          # o dispositivo está trabalhando...
    os.write(fd_escrita, b"X")  # ...e agora tem um dado pronto


def experimento(modo):
    leitura, escrita = os.pipe()
    if modo == "polling":
        os.set_blocking(leitura, False)
    threading.Thread(target=dispositivo, args=(escrita,)).start()
    cpu0, t0, consultas = time.process_time(), time.perf_counter(), 0
    if modo == "polling":
        while True:                       # espera ocupada
            consultas += 1
            try:
                os.read(leitura, 1)       # "está pronto?"
                break
            except BlockingIOError:       # "ainda não..."
                pass
    else:
        os.read(leitura, 1)               # bloqueia: o kernel nos acorda
        consultas = 1
    tempo, cpu = time.perf_counter() - t0, time.process_time() - cpu0
    os.close(leitura)
    os.close(escrita)
    return tempo, cpu, consultas


titulo("Polling × interrupção (o dispositivo fica pronto em %.0f s)" % ESPERA)
print("%-28s %10s %12s %16s" % ("estratégia", "espera", "CPU gasta", "consultas"))
for modo, nome in (("polling", "polling (espera ocupada)"),
                   ("interrupcao", "bloqueio + interrupção")):
    tempo, cpu, n = experimento(modo)
    print("%-28s %9.2fs %11.3fs %16s" % (nome, tempo, cpu, format(n, ",").replace(",", ".")))

titulo("Interrupções reais acontecendo agora neste computador")
if LINUX:
    def ler():
        cont = {}
        with open("/proc/interrupts") as f:
            ncpus = len(f.readline().split())
            for linha in f:
                partes = linha.split()
                if not partes:
                    continue
                nome = partes[0].rstrip(":")
                nums = [int(p) for p in partes[1:1 + ncpus] if p.isdigit()]
                desc = " ".join(partes[1 + len(nums):])[:38]
                cont[nome] = (sum(nums), desc)
        return cont
    a = ler()
    print("Medindo por 3 segundos (mexa o mouse, digite, abra uma página)...")
    time.sleep(3)
    b = ler()
    deltas = sorted(((b[k][0] - a.get(k, (0, ""))[0], k, b[k][1]) for k in b), reverse=True)
    print("%-6s %10s  %s" % ("IRQ", "em 3 s", "origem"))
    for d, k, desc in deltas[:10]:
        if d > 0:
            print("%-6s %10d  %s" % (k, d, desc))
    nota("LOC = temporizador local (gera a preempção do escalonador); NMI = não mascarável")
    nota("lista completa: cat /proc/interrupts")
elif MAC:
    nota("o macOS não expõe contadores de interrupção para usuários comuns.")
    nota("com senha de administrador: sudo powermetrics --samplers interrupts -i 1000 -n 1")
