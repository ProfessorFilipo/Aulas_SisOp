# -*- coding: utf-8 -*-
"""
Custo de CPU de uma requisição de E/S, conforme o modo de conclusão.

Implementem:
    núcleo (N2): polling e interrupcao
    módulo M3:   dma

Referência: Silberschatz, 9ª ed., 13.2.1 (Polling), 13.2.2 (Interrupts), 13.2.3 (DMA).

REGRAS DO MODELO (parametros.py):
- polling: a CPU fica em espera ocupada, testando o registrador de estado, durante TODO
  o atendimento da requisição (a cópia dos dados acontece dentro desse tempo):
      duracao_ms
- interrupcao: E/S programada com interrupção — a controladora interrompe a CPU a cada
  bloco transferido, e a CPU copia o bloco:
      n_blocos * (CUSTO_INTERRUPCAO_MS + CUSTO_COPIA_MS_POR_BLOCO)
- dma: a CPU programa a controladora de DMA, que copia sozinha todos os blocos e gera
  UMA interrupção no fim:
      CUSTO_PROGRAMAR_DMA_MS + CUSTO_INTERRUPCAO_MS
"""
from simes import parametros as P

MODOS = ("polling", "interrupcao", "dma")


def custo_cpu(modo, n_blocos, duracao_ms):
    """Devolve o tempo de CPU (ms) gasto com uma requisição de n_blocos que o dispositivo
    levou duracao_ms para atender."""
    if modo == "polling":
        raise NotImplementedError("TODO (núcleo N2): custo do polling")
    if modo == "interrupcao":
        raise NotImplementedError("TODO (núcleo N2): custo da interrupção")
    if modo == "dma":
        raise NotImplementedError("TODO (M3): custo do DMA")
    raise ValueError("modo desconhecido: %s" % modo)
