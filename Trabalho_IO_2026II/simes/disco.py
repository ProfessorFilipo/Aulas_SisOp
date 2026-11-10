# -*- coding: utf-8 -*-
"""
Modelos de dispositivo de armazenamento.

DiscoHDD  — FORNECIDO. Implementa o modelo de custo descrito em parametros.py.
DiscoFlash — BÔNUS. Armazenamento flash (SSD, celulares): implementem se quiserem o bônus.

Todo dispositivo oferece:
    atender(bloco, n_blocos, tipo) -> (duracao_ms, distancia_cilindros)
    mover(cilindro)                -> (duracao_ms, distancia_cilindros)
    cilindro_atual                 (atributo)
"""
from simes import parametros as P


def cilindro_do_bloco(bloco):
    return bloco // P.BLOCOS_POR_CILINDRO


class DiscoHDD:
    nome = "hdd"

    def __init__(self, busca_minima_ms=P.BUSCA_MINIMA_MS,
                 busca_por_cilindro_ms=P.BUSCA_POR_CILINDRO_MS,
                 latencia_rotacional_ms=P.LATENCIA_ROTACIONAL_MS,
                 transferencia_ms_por_bloco=P.TRANSFERENCIA_MS_POR_BLOCO,
                 cilindros=P.CILINDROS, cilindro_inicial=0, nome=None):
        self.busca_minima_ms = busca_minima_ms
        self.busca_por_cilindro_ms = busca_por_cilindro_ms
        self.latencia_rotacional_ms = latencia_rotacional_ms
        self.transferencia_ms_por_bloco = transferencia_ms_por_bloco
        self.cilindros = cilindros
        self.cilindro_atual = cilindro_inicial
        self.ultimo_bloco = None          # último bloco transferido (para detectar sequência)
        self.deslocamento_total = 0       # cilindros percorridos pelo braço
        if nome:
            self.nome = nome

    def tempo_busca(self, distancia):
        if distancia == 0:
            return 0.0
        return self.busca_minima_ms + distancia * self.busca_por_cilindro_ms

    def mover(self, cilindro):
        """Leva o braço até um cilindro sem transferir dados (usado pelo SCAN e pelo C-SCAN)."""
        distancia = abs(cilindro - self.cilindro_atual)
        duracao = self.tempo_busca(distancia)
        self.cilindro_atual = cilindro
        self.ultimo_bloco = None
        self.deslocamento_total += distancia
        return duracao, distancia

    def atender(self, bloco, n_blocos=1, tipo="L"):
        cilindro = cilindro_do_bloco(bloco)
        distancia = abs(cilindro - self.cilindro_atual)
        duracao = self.tempo_busca(distancia)
        em_sequencia = self.ultimo_bloco is not None and bloco == self.ultimo_bloco + 1
        if not em_sequencia:
            duracao += self.latencia_rotacional_ms
        duracao += n_blocos * self.transferencia_ms_por_bloco
        ultimo = bloco + n_blocos - 1
        self.cilindro_atual = cilindro_do_bloco(ultimo)
        self.ultimo_bloco = ultimo
        self.deslocamento_total += distancia
        return duracao, distancia


def criar_disco(nome):
    """Fábrica usada pelos simuladores e pelos experimentos."""
    if nome == "hdd":
        return DiscoHDD()
    if nome == "rapido":
        return DiscoHDD(nome="rapido", **P.DISPOSITIVO_RAPIDO)
    if nome == "flash":
        return DiscoFlash()
    raise ValueError("dispositivo desconhecido: %s" % nome)


# ======================================================================
# BÔNUS — armazenamento flash
# ======================================================================
class DiscoFlash:
    """
    Simula um SSD com uma camada de tradução simples (FTL) do tipo log:

    - uma página flash = um bloco lógico de 4 KiB;
    - páginas são agrupadas em blocos apagáveis de FLASH_PAGINAS_POR_BLOCO_APAGAVEL páginas;
    - uma página só pode ser gravada se estiver apagada; apagar só é possível por bloco inteiro;
    - regravar um bloco lógico grava em uma página livre nova e invalida a antiga;
    - quando faltam páginas livres, a coleta de lixo escolhe um bloco apagável, copia as
      páginas ainda válidas para outro lugar e apaga o bloco.

    Não há busca nem latência rotacional. Tempos em parametros.py (FLASH_*).
    Indicadores que o dispositivo deve expor (atributos):
        paginas_gravadas_host      páginas pedidas pelo sistema
        paginas_programadas        páginas efetivamente gravadas (inclui cópias da coleta de lixo)
        apagamentos                blocos apagados
    Amplificação de escrita = paginas_programadas / paginas_gravadas_host.
    """
    nome = "flash"

    def __init__(self, total_blocos_logicos=P.TOTAL_BLOCOS):
        self.cilindro_atual = 0
        self.deslocamento_total = 0
        self.paginas_gravadas_host = 0
        self.paginas_programadas = 0
        self.apagamentos = 0
        raise NotImplementedError("BÔNUS: implementem o DiscoFlash")

    def mover(self, cilindro):
        return 0.0, 0

    def atender(self, bloco, n_blocos=1, tipo="L"):
        raise NotImplementedError("BÔNUS: implementem o DiscoFlash")
