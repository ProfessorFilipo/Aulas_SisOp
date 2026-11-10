# -*- coding: utf-8 -*-
"""Testes do que já vem pronto (devem passar desde o início)."""
import unittest

from simes import parametros as P
from simes.disco import DiscoHDD
from simes.es.escalonadores import FCFS, percorrer
from simes.arquivos.alocacao import AlocadorContiguo
from simes.arquivos.estruturas import FCB

FILA_LIVRO = [98, 183, 37, 122, 14, 124, 65, 67]   # Silberschatz, seção 10.4


class TesteDisco(unittest.TestCase):
    def test_custo_aleatorio_e_sequencial(self):
        d = DiscoHDD()
        t, dist = d.atender(10 * P.BLOCOS_POR_CILINDRO, 2)
        self.assertEqual(dist, 10)
        self.assertAlmostEqual(t, P.BUSCA_MINIMA_MS + 10 * P.BUSCA_POR_CILINDRO_MS
                               + P.LATENCIA_ROTACIONAL_MS + 2 * P.TRANSFERENCIA_MS_POR_BLOCO)
        t, dist = d.atender(10 * P.BLOCOS_POR_CILINDRO + 2, 1)      # bloco seguinte: sem rotação
        self.assertEqual(dist, 0)
        self.assertAlmostEqual(t, P.TRANSFERENCIA_MS_POR_BLOCO)


class TesteFCFS(unittest.TestCase):
    def test_exemplo_do_livro(self):
        ordem, total = percorrer(FCFS(), FILA_LIVRO, 53)
        self.assertEqual(ordem, FILA_LIVRO)
        self.assertEqual(total, 640)


class TesteAlocadorContiguo(unittest.TestCase):
    def test_realocacao(self):
        a = AlocadorContiguo(20)
        f1, f2 = FCB(1, "f1", "arquivo", 0), FCB(2, "f2", "arquivo", 0)
        a.alocar(f1, 3)
        a.alocar(f2, 3)                         # f2 logo depois de f1
        extras = a.estender(f1, 2)              # não cabe no lugar: realoca
        self.assertEqual(a.realocacoes, 1)
        self.assertEqual(len(f1.blocos), 5)
        self.assertEqual(len(extras), 6)        # 3 leituras + 3 escritas


if __name__ == "__main__":
    unittest.main()
