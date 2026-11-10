# -*- coding: utf-8 -*-
"""Requisição de E/S de bloco. FORNECIDO."""
from simes import parametros as P


class Requisicao:
    """
    Uma requisição de leitura ('L') ou escrita ('E') de n_blocos consecutivos a partir de `bloco`.

    origem = 'usuario' para requisições vindas da carga; 'cache' para gravações geradas pela
    própria cache (expulsão de bloco sujo ou sincronização periódica). Requisições da cache não
    entram nas estatísticas de tempo de resposta, mas contam como escritas físicas.
    """
    __slots__ = ("id", "chegada", "processo", "tipo", "bloco", "n_blocos", "origem",
                 "cilindro", "inicio", "fim", "prazo")

    def __init__(self, id, chegada, processo, tipo, bloco, n_blocos=1, origem="usuario"):
        if tipo not in ("L", "E"):
            raise ValueError("tipo deve ser 'L' ou 'E'")
        self.id = id
        self.chegada = float(chegada)
        self.processo = processo
        self.tipo = tipo
        self.bloco = int(bloco)
        self.n_blocos = int(n_blocos)
        self.origem = origem
        self.cilindro = self.bloco // P.BLOCOS_POR_CILINDRO
        self.inicio = None          # quando o disco começou a atender
        self.fim = None             # quando terminou
        prazo = P.PRAZO_LEITURA_MS if tipo == "L" else P.PRAZO_ESCRITA_MS
        self.prazo = self.chegada + prazo    # usado pelo escalonador DEADLINE (M2)

    @property
    def espera(self):
        return None if self.inicio is None else self.inicio - self.chegada

    @property
    def resposta(self):
        return None if self.fim is None else self.fim - self.chegada

    def __repr__(self):
        return "Req(%s %s b=%d n=%d cil=%d t=%.1f)" % (self.id, self.tipo, self.bloco,
                                                       self.n_blocos, self.cilindro, self.chegada)
