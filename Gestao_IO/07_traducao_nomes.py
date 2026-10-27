#!/usr/bin/env python3
"""Tópico 13.5 — Do nome do arquivo até a controladora do dispositivo.

Gestão de Entrada e Saída — Sistemas Operacionais (PUCRS)
Prof. Filipo Novo Mór - filipomor.com - github.com/ProfessorFilipo
"""
import os
import re
import sys

from comum import LINUX, MAC, nota, rodar, titulo

caminho = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else __file__)

titulo("1. Nome -> tabela de montagem -> dispositivo")
print("Arquivo: " + caminho)
saida = rodar(["df", "-P", caminho])
dispositivo = saida.splitlines()[-1].split()[0]
ponto = saida.splitlines()[-1].split()[-1]
print("\nO prefixo mais longo do caminho na tabela de montagem é '%s'," % ponto)
print("que corresponde ao dispositivo %s" % dispositivo)
nota("tabela de montagem completa: comando 'mount'")

titulo("2. Dispositivo -> número <major, minor> -> driver")
st_arq = os.stat(caminho)
print("O arquivo está no dispositivo de número  <%d, %d>" % (os.major(st_arq.st_dev), os.minor(st_arq.st_dev)))
if os.path.exists(dispositivo):
    st_dev = os.stat(dispositivo)
    print("O nó %s tem o número  <%d, %d>" % (dispositivo, os.major(st_dev.st_rdev), os.minor(st_dev.st_rdev)))
    if st_dev.st_rdev != st_arq.st_dev:
        nota("os números diferem (comum em btrfs, ZFS e contêineres)")
maior = os.major(st_arq.st_dev)
if LINUX:
    with open("/proc/devices") as f:
        bloco = f.read().split("Block devices:")[1]
    driver = re.search(r"^\s*%d (\S+)" % maior, bloco, re.M)
    print("Major %d -> driver '%s' (em /proc/devices)" % (maior, driver.group(1) if driver else "?"))

titulo("3. Driver -> controladora no barramento")
if LINUX:
    sysfs = "/sys/dev/block/%d:%d" % (maior, os.minor(st_arq.st_dev))
    if os.path.exists(sysfs):
        print("Caminho do dispositivo na árvore de hardware:")
        partes = os.path.realpath(sysfs).replace("/sys/devices/", "").split("/")
        for nivel, parte in enumerate(partes):
            print("   " + "  " * nivel + "└─ " + parte)
        nota("pciXXXX = barramento PCI | 0000:BB:DD.F = controladora | nvme0n1/sda = disco")
elif MAC:
    info = rodar(["diskutil", "info", dispositivo], mostrar=False)
    for chave in ("Device Node", "Part of Whole", "Device / Media Name", "Protocol",
                  "Device Location", "Solid State"):
        m = re.search(r"^\s*%s:\s+(.*)$" % re.escape(chave), info, re.M)
        if m:
            print("   %-22s %s" % (chave + ":", m.group(1)))
    nota("Protocol mostra por qual barramento/protocolo a controladora fala com o disco")
