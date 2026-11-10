# -*- coding: utf-8 -*-
"""
Integração ponta a ponta (obrigatória para grupos de 4 integrantes).

Ideia: rodar uma carga do SISTEMA DE ARQUIVOS guardando o histórico dos acessos ao disco
(CamadaBloco com guardar_historico=True) e transformar esse histórico numa carga de E/S, que
então passa pela cache (M1) e pelo escalonador, no simulador de E/S. Assim dá para medir
como a organização dos arquivos no disco (alocação, diretórios) afeta o escalonamento e a
cache.

Cada item do histórico é (instante_ms, processo, tipo, bloco, n_blocos).
"""


def historico_para_requisicoes(historico):
    """Converte o histórico da CamadaBloco numa lista de Requisicao (simes.es.requisicao),
    em ordem de chegada, com ids 0, 1, 2, ... Acessos da mesma operação chegam no mesmo
    instante."""
    raise NotImplementedError("TODO (integração): converter o histórico em requisições")
