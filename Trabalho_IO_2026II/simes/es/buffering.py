# -*- coding: utf-8 -*-
"""
Módulo M3 (parte 2) — buffering entre um produtor e um dispositivo.

Referência: Silberschatz, 9ª ed., 13.4.2 (Buffering).

Cenário: um programa (produtor) gera `blocos` blocos de dados (ex.: uma câmera gravando
vídeo). Os dados vão para um dispositivo que grava um bloco em `consumo_ms`. Há `n_buffers`
buffers de UM bloco cada, e o produtor gera cada bloco DIRETAMENTE dentro de um buffer.

REGRAS DO MODELO (numere os blocos k = 1, 2, ..., blocos):
- para começar a gerar o bloco k, o produtor precisa (a) ter terminado o bloco k-1 e
  (b) ter um buffer livre. O buffer usado pelo bloco k é o liberado pelo bloco k - n_buffers
  (nos primeiros n_buffers blocos, todos os buffers estão livres no instante 0);
- gerar um bloco leva producao_ms; o tempo em que o produtor fica parado esperando por um
  buffer livre soma em bloqueio_produtor_ms;
- o dispositivo grava os blocos na ordem: começa o bloco k quando ele está pronto e quando
  terminou o bloco k-1; cada gravação leva consumo_ms; o buffer só fica livre quando a
  gravação termina;
- tempo_total_ms = instante em que o dispositivo termina de gravar o último bloco;
- utilizacao_dispositivo_pct = 100 * (blocos * consumo_ms) / tempo_total_ms.

Comparem n_buffers = 1 (buffer simples), 2 (duplo) e 3 (circular).
"""


def simular_buffering(n_buffers, producao_ms, consumo_ms, blocos):
    """Devolve dict com tempo_total_ms, bloqueio_produtor_ms e utilizacao_dispositivo_pct."""
    raise NotImplementedError("TODO (M3): simular o buffering")
