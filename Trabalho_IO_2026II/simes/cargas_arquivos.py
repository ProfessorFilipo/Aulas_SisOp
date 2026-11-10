# -*- coding: utf-8 -*-
"""
Geradores das cargas do sistema de arquivos. FORNECIDO.

Cada função devolve uma lista de linhas no formato "tempo_ms processo operacao args...".
As cargas padronizadas (pasta cargas/) foram geradas com estas funções e sementes fixas
(script gerar_cargas.py).
"""
import random

from simes import parametros as P

KIB = 1024


class _Roteiro:
    def __init__(self):
        self.t = 0.0
        self.linhas = []

    def op(self, processo, *partes, passo=0.5):
        self.linhas.append("%.1f %s %s" % (self.t, processo, " ".join(str(p) for p in partes)))
        self.t += passo

    def ler_inteiro(self, processo, caminho, tamanho, handle="h1", pedaco=4096):
        self.op(processo, "open", caminho, "r", handle)
        lido = 0
        while lido < tamanho:
            self.op(processo, "read", handle, pedaco)
            lido += pedaco
        self.op(processo, "close", handle)


def fs_compilador(semente=2026, builds=3):
    """Leituras sequenciais: um projeto com fontes e cabeçalhos compilado várias vezes."""
    rng = random.Random(semente)
    r = _Roteiro()
    for d in ("/proj", "/proj/src", "/proj/include", "/proj/build"):
        r.op("P1", "mkdir", d)
    fontes = [("/proj/src/mod%02d.c" % i, rng.randint(2 * KIB, 64 * KIB)) for i in range(40)]
    cabecalhos = [("/proj/include/h%02d.h" % i, rng.randint(1 * KIB, 8 * KIB)) for i in range(15)]
    for caminho, tam in fontes + cabecalhos:
        r.op("P1", "create", caminho, tam)
    for b in range(builds):
        proc = "P%d" % (b + 2)
        for caminho, tam in fontes:
            r.ler_inteiro(proc, caminho, tam, "h1")
            for h, tam_h in rng.sample(cabecalhos, 3):
                r.ler_inteiro(proc, h, tam_h, "h2")
            objeto = caminho.replace("/src/", "/build/").replace(".c", ".o")
            if b > 0:
                r.op(proc, "unlink", objeto)
            r.op(proc, "create", objeto, 0)
            r.op(proc, "open", objeto, "w", "h3")
            escrever = int(tam * 0.6)
            while escrever > 0:
                r.op(proc, "write", "h3", min(4096, escrever))
                escrever -= 4096
            r.op(proc, "close", "h3")
    return r.linhas


def fs_banco_dados(semente=2026, transacoes=3000):
    """Acesso direto: uma tabela de 64 MiB lida e alterada em posições aleatórias, com log."""
    rng = random.Random(semente)
    r = _Roteiro()
    tabela = 64 * KIB * KIB
    r.op("P1", "mkdir", "/db")
    r.op("P1", "create", "/db/tabela.dat", tabela)
    r.op("P1", "create", "/db/log.wal", 0)
    r.op("P1", "open", "/db/tabela.dat", "rw", "h1")
    r.op("P1", "open", "/db/log.wal", "a", "h2")
    for _ in range(transacoes):
        pos = rng.randrange(tabela // 4096) * 4096
        r.op("P1", "seek", "h1", pos)
        if rng.random() < 0.8:
            r.op("P1", "read", "h1", 4096, passo=2.0)
        else:
            r.op("P1", "write", "h1", 4096, passo=1.0)
            r.op("P1", "write", "h2", 512, passo=1.0)
    r.op("P1", "close", "h1")
    r.op("P1", "close", "h2")
    return r.linhas


def fs_profundidade(profundidade, repeticoes=20):
    """Um arquivo no fim de uma cadeia de `profundidade` diretórios, aberto várias vezes."""
    r = _Roteiro()
    caminho = ""
    for i in range(1, profundidade + 1):
        caminho += "/n%d" % i
        r.op("P1", "mkdir", caminho)
    arquivo = caminho + "/f.txt"
    r.op("P1", "create", arquivo, 4096)
    for _ in range(repeticoes):
        r.op("P2", "open", arquivo, "r", "h1")
        r.op("P2", "read", "h1", 4096)
        r.op("P2", "close", "h1")
    return r.linhas


def fs_servidor_web(semente=2026, trabalhadores=8, rodadas=40):
    """Vários processos abrindo, ao mesmo tempo, as mesmas páginas (tabelas compartilhadas)."""
    rng = random.Random(semente)
    r = _Roteiro()
    r.op("P0", "mkdir", "/www")
    paginas = [("/www/pagina%02d.html" % i, rng.randint(8 * KIB, 96 * KIB)) for i in range(12)]
    for caminho, tam in paginas:
        r.op("P0", "create", caminho, tam)
    for _ in range(rodadas):
        escolhas = {}
        for w in range(1, trabalhadores + 1):
            proc = "P%d" % w
            escolhas[proc] = rng.sample(paginas, 3)
            for k, (caminho, _) in enumerate(escolhas[proc], start=1):
                r.op(proc, "open", caminho, "r", "h%d" % k, passo=0.1)
        for proc, lista in escolhas.items():
            for k, (_, tam) in enumerate(lista, start=1):
                lido = 0
                while lido < tam:
                    r.op(proc, "read", "h%d" % k, 16384, passo=0.1)
                    lido += 16384
        for proc, lista in escolhas.items():
            for k in range(1, len(lista) + 1):
                r.op(proc, "close", "h%d" % k, passo=0.1)
    return r.linhas


def fs_links():
    """Hard links, links simbólicos, ponteiros pendentes e ciclos (M4)."""
    r = _Roteiro()
    for d in ("/dados", "/dados/sub", "/atalhos"):
        r.op("P1", "mkdir", d)
    r.op("P1", "create", "/dados/a.txt", 8192)
    r.op("P1", "create", "/dados/b.txt", 4096)
    r.op("P1", "create", "/dados/sub/c.txt", 4096)
    r.op("P1", "link", "/dados/a.txt", "/atalhos/a_rigido")
    r.op("P1", "symlink", "/dados/b.txt", "/atalhos/b_simbolico")
    r.op("P1", "symlink", "/dados", "/atalhos/dados_simbolico")
    r.op("P1", "symlink", "/atalhos", "/dados/sub/volta")          # cria um ciclo
    r.op("P1", "symlink", "/atalhos/l2", "/atalhos/l1")
    r.op("P1", "symlink", "/atalhos/l1", "/atalhos/l2")              # laço de links
    for _ in range(3):
        r.ler_inteiro("P2", "/atalhos/a_rigido", 8192)
        r.ler_inteiro("P2", "/atalhos/b_simbolico", 4096)
        r.ler_inteiro("P2", "/atalhos/dados_simbolico/sub/c.txt", 4096)
    r.op("P1", "percorrer", "/")
    r.op("P1", "unlink", "/dados/a.txt")
    r.op("P1", "unlink", "/dados/b.txt")
    r.ler_inteiro("P2", "/atalhos/a_rigido", 8192)                   # ainda funciona
    r.op("P2", "open", "/atalhos/b_simbolico", "r", "h1")            # pendente: ENOENT
    r.op("P2", "open", "/atalhos/l1", "r", "h1")                     # ELOOP
    r.op("P1", "link", "/dados", "/atalhos/dir_rigido")              # EPERM
    r.op("P2", "open", "/atalhos/dados_simbolico/sub/volta/a_rigido", "r", "h1")
    r.op("P2", "close", "h1")
    r.op("P1", "percorrer", "/")
    r.op("P1", "percorrer", "/atalhos")
    return r.linhas


def fs_protecao(semente=2026, rodadas=20):
    """Bits rwx, ACL e travas consultivas/mandatórias entre usuários (M5)."""
    rng = random.Random(semente)
    r = _Roteiro()
    r.op("P1", "usuario", "alice")
    r.op("P2", "usuario", "bob")
    r.op("P3", "usuario", "carol")
    r.op("P0", "mkdir", "/home")
    r.op("P1", "mkdir", "/home/alice")
    r.op("P1", "create", "/home/alice/notas.txt", 8192)
    r.op("P1", "create", "/home/alice/conta.txt", 4096)
    r.op("P1", "chmod", "/home/alice/notas.txt", "600")
    r.op("P1", "chmod", "/home/alice/conta.txt", "666")
    r.op("P2", "open", "/home/alice/notas.txt", "r", "h1")          # EACCES
    r.op("P2", "chmod", "/home/alice/notas.txt", "666")             # EPERM
    for i in range(10):
        r.op("P1", "setacl", "/home/alice/notas.txt", "usuario%02d" % i, "r--")
    r.op("P1", "setacl", "/home/alice/notas.txt", "bob", "r--")
    for _ in range(rodadas):
        r.ler_inteiro("P2", "/home/alice/notas.txt", 8192)          # permitido pela ACL
        r.op("P3", "open", "/home/alice/notas.txt", "r", "h1")      # EACCES
        r.op("P2", "open", "/home/alice/notas.txt", "w", "h9")      # EACCES (ACL só r)
        r.ler_inteiro("P1", "/home/alice/notas.txt", 8192)          # dona
    for _ in range(rodadas):
        r.op("P1", "open", "/home/alice/conta.txt", "rw", "h1")
        r.op("P2", "open", "/home/alice/conta.txt", "rw", "h2")
        r.op("P1", "lock", "h1")
        r.op("P2", "lock", "h2")                                     # EBUSY
        r.op("P2", "write", "h2", 100)                               # viola (consultivo) ou EBUSY
        r.op("P1", "seek", "h1", 0)
        r.op("P1", "write", "h1", rng.randint(50, 200))
        r.op("P1", "unlock", "h1")
        r.op("P2", "lock", "h2")
        r.op("P2", "seek", "h2", 0)
        r.op("P2", "write", "h2", 100)
        r.op("P1", "read", "h1", 100)                                # viola (consultivo) ou EBUSY
        r.op("P2", "unlock", "h2")
        r.op("P2", "close", "h2")
        r.op("P1", "close", "h1")
    return r.linhas


def fs_alocacao(semente=2026, total_blocos=20000):
    """Criação e remoção de muitos arquivos até encher a partição, crescimento e acessos (M6)."""
    rng = random.Random(semente)
    r = _Roteiro()
    r.op("P1", "mkdir", "/a")
    vivos = {}
    proximo = [0]

    def criar(blocos):
        nome = "/a/f%04d" % proximo[0]
        proximo[0] += 1
        r.op("P1", "create", nome, blocos * 4096 - rng.randint(0, 4095))
        vivos[nome] = blocos

    usados = 0
    while usados < 0.70 * total_blocos:
        b = rng.randint(1, 256)
        criar(b)
        usados += b
    for nome in rng.sample(sorted(vivos), int(len(vivos) * 0.4)):
        r.op("P1", "unlink", nome)
        usados -= vivos.pop(nome)
    while usados < 0.85 * total_blocos:
        b = rng.randint(1, 256)
        criar(b)
        usados += b
    candidatos = sorted(vivos)
    for nome in rng.sample(candidatos, min(60, len(candidatos))):
        r.op("P2", "open", nome, "a", "h1")
        for _ in range(rng.randint(2, 32)):
            r.op("P2", "write", "h1", 4096)
        r.op("P2", "close", "h1")
    grandes = sorted(candidatos, key=lambda n: (-vivos[n], n))[:5]
    for nome in grandes:
        r.op("P3", "open", nome, "r", "h1")
        for _ in range(100):
            r.op("P3", "seek", "h1", rng.randrange(vivos[nome]) * 4096)
            r.op("P3", "read", "h1", 4096)
        r.op("P3", "close", "h1")
        r.ler_inteiro("P3", nome, vivos[nome] * 4096, "h2", pedaco=65536)
    return r.linhas


PADRONIZADAS = {
    "fs_compilador": fs_compilador,
    "fs_banco_dados": fs_banco_dados,
    "fs_servidor_web": fs_servidor_web,
    "fs_links": fs_links,
    "fs_protecao": fs_protecao,
    "fs_alocacao": fs_alocacao,
}
