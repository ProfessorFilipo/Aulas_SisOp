#!/usr/bin/env python3
"""Tópico 13.2 — Hardware de E/S: barramentos, controladoras, portas e E/S mapeada em memória.

Gestão de Entrada e Saída — Sistemas Operacionais (PUCRS)
Prof. Filipo Novo Mór - filipomor.com - github.com/ProfessorFilipo
"""
import glob
import os
import re
import shutil

from comum import ARQUITETURA, ARM, LINUX, MAC, X86, nome_sistema, nota, rodar, titulo

titulo("1. Qual processador estou usando?")
print("Sistema: %s   |   Arquitetura: %s" % (nome_sistema(), ARQUITETURA))
if X86:
    print("x86: além da E/S mapeada em memória, a CPU tem instruções próprias")
    print("     de E/S (IN/OUT) que acessam 'portas' num espaço de endereços separado.")
elif ARM:
    print("ARM: NÃO existem instruções de E/S por portas. Os registradores das")
    print("     controladoras só são acessados como memória (E/S mapeada em memória).")

titulo("2. Dispositivos conectados aos barramentos")
if LINUX:
    if shutil.which("lspci"):
        rodar(["lspci"], max_linhas=15)
    else:
        classes = {"01": "armazenamento", "02": "rede", "03": "vídeo", "04": "multimídia",
                   "06": "ponte (bridge)", "0c": "barramento serial (USB...)"}
        devs = sorted(glob.glob("/sys/bus/pci/devices/*"))
        print("%d dispositivos PCI (lidos de /sys/bus/pci/devices):" % len(devs))
        for d in devs[:15]:
            with open(d + "/class") as f:
                cls = f.read().strip()[2:4]
            print("   %s  %s" % (os.path.basename(d), classes.get(cls, "classe 0x" + cls)))
    rodar(["lsusb"], max_linhas=10)
elif MAC:
    arvore = rodar(["ioreg", "-p", "IOService", "-w0"], mostrar=False)
    for classe, rotulo in (("IOPCIDevice", "PCI Express"), ("IOUSBHostDevice", "USB")):
        nomes = re.findall(r"\+-o (.+?)\s+<class %s\b" % classe, arvore)
        print("%s: %d dispositivo(s)" % (rotulo, len(nomes)))
        for n in nomes[:12]:
            print("   - " + n)

titulo("3. Portas de E/S e regiões de memória dos dispositivos")
if LINUX:
    for arq, desc in (("/proc/ioports", "portas de E/S (compare com a Fig. 13.2)"),
                      ("/proc/iomem", "regiões de E/S mapeada em memória")):
        try:
            with open(arq) as f:
                linhas = f.read().splitlines()
        except OSError:
            continue
        if arq.endswith("iomem"):  # esconde RAM e áreas do kernel; mostra os dispositivos
            linhas = [l for l in linhas if not re.search(r"RAM|Kernel|Reserved|ACPI|ROM", l)]
        print("%s — %s:" % (arq, desc))
        for linha in linhas[:10]:
            print("   " + linha)
        if linhas and all(l.strip().startswith("00000000-00000000") or l.strip().startswith("0000-0000")
                          for l in linhas[:10]):
            nota("endereços zerados: o kernel os esconde de usuários comuns.")
            nota("para ver os reais: sudo python3 01_hardware.py")
        print()
elif MAC:
    registro = rodar(["ioreg", "-l", "-w0"], mostrar=False)
    regioes = re.findall(r'"IODeviceMemory" = \(\((\{[^}]*\})', registro)
    print("Regiões de memória atribuídas a controladoras (IODeviceMemory, via ioreg):")
    for r in regioes[:8]:
        endereco = re.search(r'"address"=(\d+)', r)
        tamanho = re.search(r'"length"=(\d+)', r)
        if endereco and tamanho:
            print("   endereço 0x%012x   tamanho %8d bytes" % (int(endereco.group(1)), int(tamanho.group(1))))
    if not regioes:
        nota("o ioreg não listou regiões de memória nesta versão do macOS")
    if not X86:
        nota("no Apple Silicon não há tabela de portas: toda E/S é mapeada em memória.")
