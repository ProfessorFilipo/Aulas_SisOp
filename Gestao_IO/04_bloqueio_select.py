#!/usr/bin/env python3
"""Tópico 13.3.4 e 13.3.2 — E/S bloqueante, não bloqueante e select() com sockets.

Gestão de Entrada e Saída — Sistemas Operacionais (PUCRS)
Prof. Filipo Novo Mór - filipomor.com - github.com/ProfessorFilipo
"""
import errno
import os
import select
import socket
import subprocess
import sys
import threading
import time

from comum import LINUX, nota, rodar, titulo

titulo("1. E/S bloqueante: o processo vai para a fila de espera")
filho = subprocess.Popen([sys.executable, "-c", "import os; os.read(0, 1)"],
                         stdin=subprocess.PIPE)
time.sleep(0.5)
colunas = "pid,stat,wchan:22,command" if LINUX else "pid,stat,command"
rodar(["ps", "-o", colunas, "-p", str(filho.pid)])
nota("STAT 'S' = dormindo: o read() bloqueou e o processo saiu da fila de prontos")
filho.stdin.write(b"x")       # o "dispositivo" entrega o dado...
filho.stdin.close()
filho.wait()                  # ...e o processo é acordado e termina
print("  dado entregue -> o processo acordou e terminou (código %d)" % filho.returncode)

titulo("2. E/S não bloqueante: a chamada retorna na hora")
leitura, escrita = os.pipe()
os.set_blocking(leitura, False)
try:
    os.read(leitura, 100)
except BlockingIOError as e:
    print("read() sem dados -> erro %d (%s): %s" % (e.errno, errno.errorcode[e.errno], e.strerror))
nota("EAGAIN vale 11 no Linux e 35 no macOS: use sempre o nome, não o número")
os.write(escrita, b"dados")
print("read() com dados -> %r" % os.read(leitura, 100))

titulo("3. select(): esperar por VÁRIOS dispositivos sem espera ocupada")
servidor = socket.socket()
servidor.bind(("127.0.0.1", 0))   # porta livre qualquer
servidor.listen()
porta = servidor.getsockname()[1]


def cliente(nome, atraso):
    time.sleep(atraso)
    with socket.create_connection(("127.0.0.1", porta)) as s:
        time.sleep(0.3)
        s.sendall(("olá, aqui é o %s" % nome).encode())
        time.sleep(0.3)


for nome, atraso in (("cliente A", 1.0), ("cliente B", 2.2), ("cliente C", 2.5)):
    threading.Thread(target=cliente, args=(nome, atraso)).start()

monitorados, t0, atendidos = [servidor], time.perf_counter(), 0
while atendidos < 3:
    prontos, _, _ = select.select(monitorados, [], [], 0.8)   # dorme até algo acontecer
    agora = time.perf_counter() - t0
    if not prontos:
        print("[%4.1fs] select(): nada pronto (o processo dormiu, sem gastar CPU)" % agora)
    for s in prontos:
        if s is servidor:
            conexao, endereco = servidor.accept()
            monitorados.append(conexao)
            print("[%4.1fs] select(): nova conexão da porta %d" % (agora, endereco[1]))
        else:
            dados = s.recv(1024)
            if dados:
                print("[%4.1fs] select(): chegaram dados -> %s" % (agora, dados.decode()))
            else:
                monitorados.remove(s)
                s.close()
                atendidos += 1
servidor.close()
nota("socket(), bind(), listen(), accept() e select() são a interface de rede da seção 13.3.2")
