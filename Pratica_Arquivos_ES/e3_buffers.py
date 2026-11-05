# -*- coding: utf-8 -*-
"""
Estação 3 — Camadas de buffer: processo, kernel e disco
Conceitos: buffer da aplicação × cache do kernel (buffer cache) × armazenamento,
flush × fsync, semântica Unix (visibilidade), custo da durabilidade.
Silberschatz, 9ª ed.: 13.4.2–13.4.3 (Buffering, Caching) e 11.5.3 (Consistency Semantics)

O script cria um processo ESCRITOR (A) e o controla. Este processo é o LEITOR (B).
"""
import subprocess
import time

from comum import *

N_ESCRITAS = 100
BLOCO = b"x" * 4096


# ------------------------------------------------------------- processo A
def escritor(caminho, modo):
    """Recebe comandos pela entrada padrão e escreve com um arquivo bufferizado."""
    f = open(caminho, modo)              # BufferedWriter: buffer de 8 KiB no próprio processo
    for linha in sys.stdin:
        cmd, _, arg = linha.strip().partition(" ")
        if cmd == "escrever":
            f.write((arg + "\n").encode("utf-8"))
        elif cmd == "flush":
            f.flush()                    # buffer do processo -> kernel
        elif cmd == "fsync":
            f.flush()
            os.fsync(f.fileno())         # kernel -> dispositivo
        print("ok", flush=True)


class ProcessoA:
    def __init__(self, caminho, modo):
        self.p = subprocess.Popen([sys.executable, os.path.abspath(__file__), "--escritor",
                                   caminho, modo], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, universal_newlines=True,
                                  encoding="utf-8", bufsize=1)
        mostrar("Processo A (escritor) iniciado, PID", self.p.pid)

    def enviar(self, comando):
        t0 = time.perf_counter()
        self.p.stdin.write(comando + "\n")
        self.p.stdin.flush()
        self.p.stdout.readline()
        return time.perf_counter() - t0

    def matar(self):
        self.p.kill()
        self.p.wait()
        mostrar("Processo A foi MORTO (kill), código de saída", self.p.returncode)


def visao_de_b(caminho):
    with open(caminho, "rb") as f:
        dados = f.read()
    mostrar("B vê %d bytes no arquivo:" % len(dados), repr(dados.decode("utf-8", "replace")))


# ---------------------------------------------------------------- custo
def medir(caminho, com_fsync, full=False):
    fd = os.open(caminho, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | O_BINARY)
    t0 = time.perf_counter()
    for _ in range(N_ESCRITAS):
        os.write(fd, BLOCO)
        if full:
            import fcntl
            fcntl.fcntl(fd, getattr(fcntl, "F_FULLFSYNC", 51))
        elif com_fsync:
            os.fsync(fd)
    dt = time.perf_counter() - t0
    os.close(fd)
    return dt


def main():
    estacao(3, "Camadas de buffer: processo, kernel e disco", "13.4.2, 13.4.3 e 11.5.3")
    d = pasta("e3")
    arq = os.path.join(d, "diario.txt")

    passo("1. A escreve uma linha, sem flush")
    a = ProcessoA(arq, "wb")
    a.enviar("escrever Linha 1")
    prever("A escreveu 'Linha 1' mas não chamou flush(). "
           "Se B (este processo) ler o arquivo agora, o que encontrará?")
    visao_de_b(arq)

    passo("2. A chama flush() — mas não fsync()")
    prever("Depois do flush(), B verá a linha? Ela já está gravada no disco?")
    a.enviar("flush")
    visao_de_b(arq)

    passo("3. A chama fsync()")
    prever("O que muda para B depois do fsync()? Quanto tempo vocês acham que ele leva?")
    dt = a.enviar("fsync")
    visao_de_b(arq)
    mostrar("Tempo do fsync() (com ida e volta do comando):", "%.2f ms" % (dt * 1000))

    passo("4. Queda do PROCESSO sem flush")
    a.enviar("escrever Linha 2 (sem flush)")
    prever("A escreveu 'Linha 2' sem flush e será morto agora. A Linha 2 sobrevive?")
    a.matar()
    visao_de_b(arq)

    passo("5. Queda do PROCESSO depois do flush")
    a = ProcessoA(arq, "ab")
    a.enviar("escrever Linha 3 (com flush)")
    a.enviar("flush")
    prever("Agora A escreveu 'Linha 3', chamou flush() e será morto. A Linha 3 sobrevive?")
    a.matar()
    visao_de_b(arq)
    if LINUX:
        try:
            with open("/proc/sys/vm/dirty_expire_centisecs") as f:
                cs = int(f.read())
            mostrar("Linux: tempo máximo de um dado 'sujo' no cache:", "%.0f s" % (cs / 100.0))
        except OSError:
            pass

    passo("6. O preço da durabilidade")
    prever("Vamos fazer %d escritas de 4 KiB: (a) só write(); (b) write() + fsync() a cada uma. "
           "Quantas vezes mais lento será (b)?" % N_ESCRITAS)
    alvo = os.path.join(d, "custo.bin")
    t_a = medir(alvo, False)
    t_b = medir(alvo, True)
    mostrar("(a) só write():", "%8.1f ms  (%9.0f escritas/s)" % (t_a * 1000, N_ESCRITAS / t_a))
    mostrar("(b) write() + fsync():", "%8.1f ms  (%9.0f escritas/s)" % (t_b * 1000, N_ESCRITAS / t_b))
    mostrar("(b) ÷ (a):", "%.0f vezes" % (t_b / t_a if t_a else 0))
    if MAC:
        t_c = medir(alvo, True, full=True)
        mostrar("(c) write() + F_FULLFSYNC:", "%8.1f ms  (%9.0f escritas/s)" % (t_c * 1000, N_ESCRITAS / t_c))
        nota("No macOS, fsync() entrega os dados ao disco, mas não esvazia o cache interno\n"
             "do próprio dispositivo. F_FULLFSYNC faz isso. Comparem (b) e (c).")
    os.remove(alvo)

    discutir("Em que camada estava a Linha 2 quando A morreu? E a Linha 3?",
             "Se, em vez do processo, faltasse ENERGIA logo após o flush(), a Linha 3 sobreviveria?",
             "A Linha 1 ficou visível para B antes do fsync(). Que semântica de consistência é essa?",
             "Por que bancos de dados chamam fsync() mesmo sendo tão caro? (Lista, Questão 10)")
    fim("e4_volumes.py")


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--escritor":
        escritor(sys.argv[2], sys.argv[3])
    else:
        main()
