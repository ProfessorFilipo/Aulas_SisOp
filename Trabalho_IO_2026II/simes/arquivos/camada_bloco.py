# -*- coding: utf-8 -*-
"""
Camada de blocos usada pelo sistema de arquivos. FORNECIDO.

Executa os acessos ao disco em ordem, um após o outro (sem fila nem escalonador): blocos
consecutivos são agrupados numa única requisição ao disco, que então não paga a latência
rotacional entre eles. Contabiliza leituras, escritas e tempo, e guarda o histórico dos
acessos (usado na integração ponta a ponta).

Um ACESSO = um bloco lido ou gravado.
"""


class CamadaBloco:
    def __init__(self, disco, guardar_historico=False):
        self.disco = disco
        self.leituras = 0
        self.escritas = 0
        self.tempo_ms = 0.0
        self.guardar_historico = guardar_historico
        self.historico = []          # (instante_ms, processo, tipo, bloco, n_blocos)
        self.instante_ms = 0.0       # atualizado pelo simulador antes de cada operação
        self.processo = "P0"

    @property
    def acessos(self):
        return self.leituras + self.escritas

    def ler(self, blocos):
        self._acessar("L", blocos)

    def escrever(self, blocos):
        self._acessar("E", blocos)

    def _acessar(self, tipo, blocos):
        blocos = list(blocos)
        i = 0
        while i < len(blocos):
            j = i
            while j + 1 < len(blocos) and blocos[j + 1] == blocos[j] + 1:
                j += 1
            inicio, n = blocos[i], j - i + 1
            duracao, _ = self.disco.atender(inicio, n, tipo)
            self.tempo_ms += duracao
            if tipo == "L":
                self.leituras += n
            else:
                self.escritas += n
            if self.guardar_historico:
                self.historico.append((self.instante_ms, self.processo, tipo, inicio, n))
            i = j + 1
