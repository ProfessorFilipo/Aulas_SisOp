# -*- coding: utf-8 -*-
"""Testes dos módulos M1–M6 e da integração. São pulados enquanto o módulo não existir."""
import unittest

from simes import parametros as P
from simes.arquivos.estruturas import FCB, ErroSA
from simes.arquivos.simulador import montar_sistema
from simes.es.requisicao import Requisicao

FILA_LIVRO = [98, 183, 37, 122, 14, 124, 65, 67]


class BaseModulo(unittest.TestCase):
    def exigir(self, funcao, *args, **kw):
        try:
            return funcao(*args, **kw)
        except NotImplementedError as e:
            self.skipTest("não implementado: %s" % e)


class TesteM1Cache(BaseModulo):
    def test_lru_e_fifo(self):
        from simes.es.cache import CacheFIFO, CacheLRU
        lru = self.exigir(CacheLRU, 2, "write-through")
        lru.inserir(1)
        lru.inserir(2)
        self.assertTrue(lru.ler(1))          # 1 vira o mais recente
        lru.inserir(3)                       # expulsa 2
        self.assertFalse(lru.ler(2))
        self.assertTrue(lru.ler(1))
        fifo = self.exigir(CacheFIFO, 2, "write-through")
        fifo.inserir(1)
        fifo.inserir(2)
        fifo.ler(1)                          # não muda a ordem
        fifo.inserir(3)                      # expulsa 1
        self.assertFalse(fifo.ler(1))

    def test_politicas_de_escrita(self):
        from simes.es.cache import CacheLRU
        wt = self.exigir(CacheLRU, 4, "write-through")
        self.assertEqual(wt.escrever(7), [7])
        self.assertEqual(wt.sujos(), 0)
        wb = self.exigir(CacheLRU, 1, "write-back")
        self.assertEqual(wb.escrever(7), [])
        self.assertEqual(wb.sujos(), 1)
        self.assertEqual(wb.escrever(8), [7])                 # 7 sujo é expulso
        self.assertEqual(wb.sincronizar(), [8])
        self.assertEqual(wb.sujos(), 0)


class TesteM2Escalonadores(BaseModulo):
    def test_livro(self):
        from simes.es.escalonadores import CLOOK, CSCAN, LOOK, percorrer
        self.assertEqual(self.exigir(percorrer, CSCAN(), FILA_LIVRO, 53)[1], 382)
        self.assertEqual(self.exigir(percorrer, LOOK(), FILA_LIVRO, 53)[1], 299)
        self.assertEqual(self.exigir(percorrer, CLOOK(), FILA_LIVRO, 53)[1], 322)

    def test_deadline(self):
        from simes.es.escalonadores import Deadline
        velha = Requisicao(0, 0.0, "P1", "L", 4000 * P.BLOCOS_POR_CILINDRO)
        perto = Requisicao(1, 900.0, "P1", "L", 101 * P.BLOCOS_POR_CILINDRO)
        i, _, _ = self.exigir(Deadline().escolher, [velha, perto], 100, +1, 100.0, 4999)
        self.assertEqual(i, 1)                                  # prazo não venceu: SSTF
        i, _, _ = Deadline().escolher([velha, perto], 100, +1, 1000.0, 4999)
        self.assertEqual(i, 0)                                  # prazo vencido: a mais antiga


class TesteM3DMAeBuffering(BaseModulo):
    def test_dma(self):
        from simes.es.cpu import custo_cpu
        self.assertAlmostEqual(self.exigir(custo_cpu, "dma", 64, 10.0),
                               P.CUSTO_PROGRAMAR_DMA_MS + P.CUSTO_INTERRUPCAO_MS)

    def test_buffering(self):
        from simes.es.buffering import simular_buffering
        r1 = self.exigir(simular_buffering, 1, 2.0, 8.0, 100)
        self.assertAlmostEqual(r1["tempo_total_ms"], 100 * (2.0 + 8.0))
        r2 = simular_buffering(2, 2.0, 8.0, 100)
        self.assertAlmostEqual(r2["tempo_total_ms"], 2.0 + 100 * 8.0)


class TesteM4Links(BaseModulo):
    def test_links(self):
        sa = montar_sistema("contigua", total_blocos=5000)
        sa.mkdir("P1", "/d")
        sa.create("P1", "/d/a", 4096)
        self.exigir(sa.link, "P1", "/d/a", "/d/a2")
        self.assertEqual(sa.resolver("/d/a").links, 2)
        sa.symlink("P1", "/d/a", "/d/s")
        self.assertIs(sa.resolver("/d/s"), sa.resolver("/d/a"))
        sa.unlink("P1", "/d/a")
        self.assertEqual(sa.resolver("/d/a2").links, 1)
        with self.assertRaises(ErroSA) as ctx:
            sa.open("P1", "/d/s", "r", "h")
        self.assertEqual(ctx.exception.codigo, "ENOENT")
        sa.symlink("P1", "/d/y", "/d/x")
        sa.symlink("P1", "/d/x", "/d/y")
        with self.assertRaises(ErroSA) as ctx:
            sa.open("P1", "/d/x", "r", "h")
        self.assertEqual(ctx.exception.codigo, "ELOOP")
        sa.symlink("P1", "/", "/d/raiz")                         # ciclo
        sa.percorrer("P1", "/")
        self.assertGreaterEqual(sa.contadores["ciclos_detectados"], 1)


class TesteM5Protecao(BaseModulo):
    def test_permissoes_e_travas(self):
        sa = montar_sistema("contigua", total_blocos=5000, bloqueio="mandatorio")
        self.exigir(sa.usuario, "P1", "alice")
        sa.usuario("P2", "bob")
        sa.mkdir("P1", "/h")
        sa.create("P1", "/h/f", 4096)
        sa.chmod("P1", "/h/f", "600")
        with self.assertRaises(ErroSA) as ctx:
            sa.open("P2", "/h/f", "r", "h")
        self.assertEqual(ctx.exception.codigo, "EACCES")
        sa.setacl("P1", "/h/f", "bob", "rw-")
        sa.open("P2", "/h/f", "rw", "h")
        sa.open("P1", "/h/f", "rw", "h")
        sa.lock("P1", "h")
        with self.assertRaises(ErroSA) as ctx:
            sa.write("P2", "h", 10)
        self.assertEqual(ctx.exception.codigo, "EBUSY")


class TesteM6Alocacao(BaseModulo):
    def test_custos_de_acesso(self):
        from simes.arquivos.alocacao import AlocadorEncadeado, AlocadorFAT, AlocadorIndexado
        enc = AlocadorEncadeado(5000)
        f = FCB(1, "f", "arquivo", 0)
        self.exigir(enc.alocar, f, 10)
        self.assertEqual(len(enc.bloco_fisico(f, 5)[1]), 5)     # lê os 5 anteriores
        self.assertEqual(len(enc.bloco_fisico(f, 6)[1]), 0)     # o seguinte: nada
        fat = AlocadorFAT(5000)
        g = FCB(2, "g", "arquivo", 0)
        self.exigir(fat.alocar, g, 10)
        self.assertEqual(fat.bloco_fisico(g, 9)[1], [])
        ind = AlocadorIndexado(5000)
        h = FCB(3, "h", "arquivo", 0)
        self.exigir(ind.alocar, h, 10)
        self.assertEqual(len(ind.bloco_fisico(h, 9)[1]), 1)
        k = FCB(4, "k", "arquivo", 0)
        ind.alocar(k, 2000)
        self.assertEqual(len(ind.bloco_fisico(k, 1500)[1]), 2)


class TesteIntegracao(BaseModulo):
    def test_historico(self):
        from simes.integracao import historico_para_requisicoes
        reqs = self.exigir(historico_para_requisicoes, [(5.0, "P1", "L", 10, 2), (1.0, "P2", "E", 99, 1)])
        self.assertEqual([(r.chegada, r.bloco, r.n_blocos, r.tipo) for r in reqs],
                         [(1.0, 99, 1, "E"), (5.0, 10, 2, "L")])
        self.assertEqual([r.id for r in reqs], [0, 1])


if __name__ == "__main__":
    unittest.main()
