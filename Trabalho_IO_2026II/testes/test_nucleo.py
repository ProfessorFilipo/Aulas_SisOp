# -*- coding: utf-8 -*-
"""Testes do núcleo (N2 e N3). Falham até vocês implementarem o núcleo."""
import unittest

from simes import parametros as P
from simes.es.cpu import custo_cpu
from simes.es.escalonadores import SCAN, SSTF, percorrer
from simes.arquivos.estruturas import ErroSA
from simes.arquivos.simulador import montar_sistema

FILA_LIVRO = [98, 183, 37, 122, 14, 124, 65, 67]


class TesteEscalonadores(unittest.TestCase):
    def test_sstf_livro(self):
        ordem, total = percorrer(SSTF(), FILA_LIVRO, 53)
        self.assertEqual(ordem, [65, 67, 37, 14, 98, 122, 124, 183])
        self.assertEqual(total, 236)

    def test_scan_descendo_livro(self):
        ordem, total = percorrer(SCAN(), FILA_LIVRO, 53, direcao=-1)
        self.assertEqual(ordem, [37, 14, 65, 67, 98, 122, 124, 183])
        self.assertEqual(total, 236)

    def test_scan_subindo(self):
        ordem, total = percorrer(SCAN(), FILA_LIVRO, 53, direcao=+1)
        self.assertEqual(ordem, [65, 67, 98, 122, 124, 183, 37, 14])
        self.assertEqual(total, 331)


class TesteCPU(unittest.TestCase):
    def test_polling(self):
        self.assertAlmostEqual(custo_cpu("polling", 8, 10.0), 10.0)

    def test_interrupcao(self):
        self.assertAlmostEqual(custo_cpu("interrupcao", 8, 10.0),
                               8 * (P.CUSTO_INTERRUPCAO_MS + P.CUSTO_COPIA_MS_POR_BLOCO))


class TesteSistemaArquivos(unittest.TestCase):
    def setUp(self):
        self.sa = montar_sistema("contigua", total_blocos=10000)
        self.c = self.sa.camada

    def custo(self, funcao, *args):
        antes = (self.c.leituras, self.c.escritas)
        resultado = funcao(*args)
        return (self.c.leituras - antes[0], self.c.escritas - antes[1]), resultado

    def preparar(self):
        self.sa.mkdir("P1", "/a")
        self.sa.mkdir("P1", "/a/b")
        self.sa.create("P1", "/a/b/f.txt", 10000)

    def test_custos_de_criacao(self):
        self.assertEqual(self.custo(self.sa.mkdir, "P1", "/a")[0], (1, 2))
        self.assertEqual(self.custo(self.sa.mkdir, "P1", "/a/b")[0], (2, 2))
        self.assertEqual(self.custo(self.sa.create, "P1", "/a/b/f.txt", 10000)[0], (3, 1))
        f = self.sa.resolver("/a/b/f.txt")
        self.assertEqual((f.tamanho, len(f.blocos)), (10000, 3))

    def test_resolver_e_open(self):
        self.preparar()
        self.assertEqual(self.custo(self.sa.resolver, "/a/b/f.txt")[0], (3, 0))
        self.assertEqual(self.custo(self.sa.open, "P1", "/a/b/f.txt", "r", "h1")[0], (3, 0))
        self.assertEqual(len(self.sa.tabela_global), 1)
        self.assertEqual(self.sa.tabelas_processo["P1"]["h1"].posicao, 0)

    def test_leitura_sequencial(self):
        self.preparar()
        self.sa.open("P1", "/a/b/f.txt", "r", "h1")
        (acessos, lidos) = self.custo(self.sa.read, "P1", "h1", 5000)
        self.assertEqual((acessos, lidos), ((2, 0), 5000))
        (acessos, lidos) = self.custo(self.sa.read, "P1", "h1", 10000)
        self.assertEqual((acessos, lidos), ((2, 0), 5000))       # para no fim do arquivo
        self.assertEqual(self.custo(self.sa.read, "P1", "h1", 100)[1], 0)

    def test_tabelas_compartilhadas(self):
        self.preparar()
        self.sa.open("P1", "/a/b/f.txt", "r", "h1")
        self.sa.open("P2", "/a/b/f.txt", "r", "h1")
        self.sa.read("P1", "h1", 4096)
        self.assertEqual(len(self.sa.tabela_global), 1)
        entrada = list(self.sa.tabela_global.values())[0]
        self.assertEqual(entrada.contador, 2)
        self.assertEqual(self.sa.tabelas_processo["P1"]["h1"].posicao, 4096)
        self.assertEqual(self.sa.tabelas_processo["P2"]["h1"].posicao, 0)
        self.sa.close("P1", "h1")
        self.assertEqual(entrada.contador, 1)
        self.sa.close("P2", "h1")
        self.assertEqual(len(self.sa.tabela_global), 0)

    def test_escrita_extensao_e_close(self):
        self.preparar()
        self.sa.open("P1", "/a/b/f.txt", "w", "h2")
        self.assertEqual(self.custo(self.sa.write, "P1", "h2", 8192)[0], (0, 2))
        self.sa.seek("P1", "h2", 12000)
        self.assertEqual(self.custo(self.sa.write, "P1", "h2", 1000)[0], (0, 2))
        f = self.sa.resolver("/a/b/f.txt")
        self.assertEqual((f.tamanho, len(f.blocos)), (13000, 4))
        self.assertEqual(self.custo(self.sa.close, "P1", "h2")[0], (0, 1))   # FCB sujo

    def test_modo_acrescimo(self):
        self.preparar()
        self.sa.open("P1", "/a/b/f.txt", "a", "h1")
        self.sa.write("P1", "h1", 100)
        self.assertEqual(self.sa.resolver("/a/b/f.txt").tamanho, 10100)

    def test_unlink_com_arquivo_aberto(self):
        self.preparar()
        livres = self.sa.alocador.bitmap.livres()
        self.sa.open("P3", "/a/b/f.txt", "r", "h")
        self.assertEqual(self.custo(self.sa.unlink, "P1", "/a/b/f.txt")[0], (3, 1))
        self.assertEqual(self.sa.read("P3", "h", 4096), 4096)                 # ainda dá para ler
        self.assertEqual(self.sa.alocador.bitmap.livres(), livres)            # blocos ainda ocupados
        self.sa.close("P3", "h")
        self.assertEqual(self.sa.alocador.bitmap.livres(), livres + 3)        # liberados no close

    def test_erros(self):
        self.preparar()

        def codigo(funcao, *args):
            with self.assertRaises(ErroSA) as ctx:
                funcao(*args)
            return ctx.exception.codigo

        self.assertEqual(codigo(self.sa.open, "P1", "/nao/existe", "r", "h"), "ENOENT")
        self.assertEqual(codigo(self.sa.mkdir, "P1", "/a"), "EEXIST")
        self.assertEqual(codigo(self.sa.create, "P1", "/a/b/f.txt/x", 1), "ENOTDIR")
        self.assertEqual(codigo(self.sa.open, "P1", "/a/b", "r", "h"), "EISDIR")
        self.assertEqual(codigo(self.sa.close, "P1", "nenhum"), "EBADF")
        self.sa.open("P1", "/a/b/f.txt", "r", "h")
        self.assertEqual(codigo(self.sa.write, "P1", "h", 10), "EBADF")
        self.assertEqual(codigo(self.sa.seek, "P1", "h", -1), "EINVAL")


if __name__ == "__main__":
    unittest.main()
