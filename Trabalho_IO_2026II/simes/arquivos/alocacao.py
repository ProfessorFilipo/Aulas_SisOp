# -*- coding: utf-8 -*-
"""
Alocação de blocos e gerenciamento do espaço livre.

FORNECIDO: Bitmap (espaço livre) e AlocadorContiguo (usado no núcleo).
MÓDULO M6 (pesquisa — Silberschatz, 9ª ed., 12.4 e 12.5): AlocadorEncadeado, AlocadorFAT
e AlocadorIndexado.

INTERFACE de todo alocador (o sistema de arquivos só usa estes métodos):

    alocar(fcb, n)        reserva n blocos de dados para um arquivo novo e define fcb.blocos
    estender(fcb, n)      acrescenta n blocos ao fim de um arquivo
    liberar(fcb)          devolve ao espaço livre todos os blocos do arquivo
    bloco_fisico(fcb, i)  -> (bloco, extras): bloco físico do i-ésimo bloco lógico do arquivo
    metricas()            -> dict de indicadores do alocador

`alocar`, `estender` e `bloco_fisico` devolvem `extras`: a lista de acessos ADICIONAIS que a
operação exige no disco, na forma [('L', bloco), ('E', bloco), ...] — por exemplo, ler blocos
de ponteiros ou de índice, ou copiar blocos numa realocação. O sistema de arquivos executa
esses acessos (método _aplicar). Sem espaço suficiente: lancem ErroSA('ENOSPC') e somem 1 em
self.falhas.
"""
import re

from simes.arquivos.estruturas import ErroSA


class Bitmap:
    """Mapa de bits do espaço livre: 0 = livre, 1 = ocupado (Silberschatz 12.5.1)."""

    def __init__(self, total):
        self.total = total
        self.mapa = bytearray(total)
        self.ocupados = 0

    def livre(self, bloco):
        return self.mapa[bloco] == 0

    def ocupar(self, blocos):
        for b in blocos:
            if self.mapa[b]:
                raise RuntimeError("bloco %d já ocupado" % b)
            self.mapa[b] = 1
            self.ocupados += 1

    def liberar(self, blocos):
        for b in blocos:
            if self.mapa[b]:
                self.mapa[b] = 0
                self.ocupados -= 1

    def livres(self):
        return self.total - self.ocupados

    def intervalo_livre(self, inicio, n):
        if inicio + n > self.total:
            return False
        return self.mapa.find(1, inicio, inicio + n) == -1

    def primeiro_encaixe(self, n):
        """Início do primeiro trecho de n blocos livres CONTÍGUOS, ou None (first-fit)."""
        if n <= 0:
            return 0
        pos = self.mapa.find(bytes(n))
        return None if pos < 0 else pos

    def primeiros_livres(self, n, a_partir_de=0):
        """Os n primeiros blocos livres (não necessariamente contíguos), ou None."""
        if n > self.livres():
            return None
        res, pos = [], a_partir_de
        while len(res) < n:
            pos = self.mapa.find(0, pos)
            if pos < 0:
                if a_partir_de:
                    return self.primeiros_livres(n, 0)
                return None
            res.append(pos)
            pos += 1
        return res

    def segmentos_livres(self):
        """Lista dos tamanhos dos trechos livres contíguos."""
        return [m.end() - m.start() for m in re.finditer(b"\x00+", bytes(self.mapa))]


class Alocador:
    nome = "?"

    def __init__(self, total_blocos):
        self.bitmap = Bitmap(total_blocos)
        self.realocacoes = 0
        self.falhas = 0

    def alocar(self, fcb, n):
        raise NotImplementedError

    def estender(self, fcb, n):
        raise NotImplementedError

    def liberar(self, fcb):
        self.bitmap.liberar(fcb.blocos)
        fcb.blocos = []

    def bloco_fisico(self, fcb, i):
        raise NotImplementedError

    def metricas(self):
        seg = self.bitmap.segmentos_livres()
        return {
            "blocos_livres": self.bitmap.livres(),
            "segmentos_livres": len(seg),
            "maior_segmento_livre": max(seg) if seg else 0,
            "realocacoes": self.realocacoes,
            "falhas_alocacao": self.falhas,
        }


class AlocadorContiguo(Alocador):
    """
    Alocação contígua com primeiro encaixe (first-fit). FORNECIDO.
    - estender: se os blocos logo depois do fim do arquivo estão livres, cresce no lugar;
      senão, REALOCA o arquivo inteiro para um trecho livre grande o suficiente, copiando os
      blocos (extras = leitura de cada bloco antigo + escrita no bloco novo correspondente).
    - bloco_fisico: endereço direto (início + i), sem acessos extras.
    """
    nome = "contigua"

    def alocar(self, fcb, n):
        if n == 0:
            fcb.blocos = []
            return []
        inicio = self.bitmap.primeiro_encaixe(n)
        if inicio is None:
            self.falhas += 1
            raise ErroSA("ENOSPC", "sem %d blocos contíguos" % n)
        fcb.blocos = list(range(inicio, inicio + n))
        self.bitmap.ocupar(fcb.blocos)
        return []

    def estender(self, fcb, n):
        if n <= 0:
            return []
        if not fcb.blocos:
            return self.alocar(fcb, n)
        fim = fcb.blocos[-1] + 1
        if self.bitmap.intervalo_livre(fim, n):
            novos = list(range(fim, fim + n))
            self.bitmap.ocupar(novos)
            fcb.blocos.extend(novos)
            return []
        antigos = fcb.blocos
        total = len(antigos) + n
        inicio = self.bitmap.primeiro_encaixe(total)
        if inicio is None:
            self.falhas += 1
            raise ErroSA("ENOSPC", "sem %d blocos contíguos para realocar" % total)
        novos = list(range(inicio, inicio + total))
        self.bitmap.ocupar(novos)
        self.bitmap.liberar(antigos)
        fcb.blocos = novos
        self.realocacoes += 1
        extras = []
        for velho, novo in zip(antigos, novos):
            extras.append(("L", velho))
            extras.append(("E", novo))
        return extras

    def bloco_fisico(self, fcb, i):
        return fcb.blocos[i], []


# ====================================================================== M6
class AlocadorEncadeado(Alocador):
    """
    Alocação encadeada "pura": cada bloco de dados guarda o ponteiro para o próximo.
    - alocar/estender usam os primeiros blocos livres do disco (Bitmap.primeiros_livres);
    - estender exige 1 escrita extra no bloco que era o último (para gravar o novo ponteiro);
    - bloco_fisico(fcb, i): o alocador lembra, em fcb.extra['cursor'], o índice do último
      bloco alcançado naquele arquivo (começa em -1). Para chegar ao bloco i a partir do
      cursor c: se i > c, é preciso ler os blocos c+1 .. i-1 (para obter os ponteiros);
      se i <= c, recomeça do início e lê os blocos 0 .. i-1. Depois, cursor = i.
      (Assim, a leitura sequencial não tem extras, e o acesso direto paga a corrente.)
    """
    nome = "encadeada"

    def alocar(self, fcb, n):
        raise NotImplementedError("TODO (M6): alocação encadeada")

    def estender(self, fcb, n):
        raise NotImplementedError("TODO (M6): alocação encadeada")

    def bloco_fisico(self, fcb, i):
        raise NotImplementedError("TODO (M6): alocação encadeada")


class AlocadorFAT(Alocador):
    """
    Alocação encadeada com tabela de alocação (FAT), como nos pendrives (FAT32/exFAT).
    Mesmos blocos que a encadeada, mas os ponteiros ficam numa tabela mantida em MEMÓRIA:
    bloco_fisico e estender não têm acessos extras.
    """
    nome = "fat"

    def alocar(self, fcb, n):
        raise NotImplementedError("TODO (M6): FAT")

    def estender(self, fcb, n):
        raise NotImplementedError("TODO (M6): FAT")

    def bloco_fisico(self, fcb, i):
        raise NotImplementedError("TODO (M6): FAT")


class AlocadorIndexado(Alocador):
    """
    Alocação indexada (como os i-nodes do Unix), com blocos de índice de 1024 ponteiros:
    - até 1024 blocos de dados: 1 bloco de índice;
      mais de 1024: índice de 2 níveis = 1 bloco de 1º nível + ceil(n / 1024) blocos de 2º nível;
    - todo arquivo tem índice, mesmo vazio (n = 0); guardem a lista dos blocos de índice em
      fcb.extra['indices'] (o de 1º nível primeiro);
    - alocar: reserva primeiro os blocos de índice e depois os de dados, nos primeiros blocos
      livres do disco; extras = 1 escrita por bloco de índice;
    - estender: acrescenta os blocos de índice que faltarem e os de dados; extras = 1 escrita
      por bloco de índice do arquivo (todos, depois da extensão);
    - bloco_fisico(fcb, i): 1 leitura extra (o índice), ou 2 no índice de 2 níveis
      (o de 1º nível e o de 2º nível que aponta para o bloco i: indices[1 + i // 1024]);
    - liberar: devolve dados e índices.
    """
    nome = "indexada"

    def alocar(self, fcb, n):
        raise NotImplementedError("TODO (M6): alocação indexada")

    def estender(self, fcb, n):
        raise NotImplementedError("TODO (M6): alocação indexada")

    def liberar(self, fcb):
        raise NotImplementedError("TODO (M6): alocação indexada")

    def bloco_fisico(self, fcb, i):
        raise NotImplementedError("TODO (M6): alocação indexada")


ALOCADORES = {c.nome: c for c in (AlocadorContiguo, AlocadorEncadeado, AlocadorFAT, AlocadorIndexado)}


def criar_alocador(nome, total_blocos):
    try:
        return ALOCADORES[nome](total_blocos)
    except KeyError:
        raise ValueError("alocador desconhecido: %s" % nome)
