# -*- coding: utf-8 -*-
"""
Simulador do sistema de arquivos. FORNECIDO — não precisam alterar.

Executa uma carga de operações (cargas/fs_*.txt) sobre um SistemaArquivos e mede, por
operação, os acessos ao disco, o tempo de disco e o tamanho das tabelas de arquivos abertos.
"""
from collections import Counter, defaultdict

from simes import parametros as P
from simes.arquivos.alocacao import criar_alocador
from simes.arquivos.camada_bloco import CamadaBloco
from simes.arquivos.estruturas import ErroSA
from simes.arquivos.sistema import SistemaArquivos
from simes.disco import DiscoHDD
from simes.metricas import media


def _converter(arg):
    try:
        return int(arg)
    except ValueError:
        return arg


def montar_sistema(alocador="contigua", total_blocos=P.TOTAL_BLOCOS, bloqueio="consultivo",
                   guardar_historico=False, classe=SistemaArquivos):
    camada = CamadaBloco(DiscoHDD(), guardar_historico=guardar_historico)
    return classe(camada, criar_alocador(alocador, total_blocos), bloqueio=bloqueio)


def descontinuidades_medias(sistema):
    """Média, por arquivo com 2 ou mais blocos, de quantas vezes o bloco seguinte não é o
    vizinho físico do anterior (0 = arquivo totalmente contíguo)."""
    valores = []
    for fcb in sistema.fcbs.values():
        if fcb.tipo == "arquivo" and len(fcb.blocos) >= 2:
            quebras = sum(1 for a, b in zip(fcb.blocos, fcb.blocos[1:]) if b != a + 1)
            valores.append(quebras)
    return media(valores)


def simular_arquivos(operacoes, sistema):
    camada = sistema.camada
    por_op = defaultdict(lambda: {"n": 0, "erros": 0, "acessos": 0, "tempo": 0.0})
    erros = Counter()
    maximos = Counter()
    for tempo, processo, op, args in operacoes:
        sistema.agora_ms = tempo
        camada.instante_ms = tempo
        camada.processo = processo
        metodo = getattr(sistema, op, None)
        if metodo is None or op.startswith("_"):
            raise ValueError("operação desconhecida na carga: %s" % op)
        acessos0, tempo0 = camada.acessos, camada.tempo_ms
        registro = por_op[op]
        registro["n"] += 1
        try:
            metodo(processo, *[_converter(a) for a in args])
        except ErroSA as e:
            registro["erros"] += 1
            erros[e.codigo] += 1
        registro["acessos"] += camada.acessos - acessos0
        registro["tempo"] += camada.tempo_ms - tempo0
        tamanhos = [len(t) for t in sistema.tabelas_processo.values()]
        maximos["tabela_global"] = max(maximos["tabela_global"], len(sistema.tabela_global))
        maximos["tabela_processo"] = max(maximos["tabela_processo"], max(tamanhos, default=0))
        maximos["soma_processos"] = max(maximos["soma_processos"], sum(tamanhos))
        maximos["contador"] = max(maximos["contador"],
                                  max((e.contador for e in sistema.tabela_global.values()), default=0))

    n_ops = sum(r["n"] for r in por_op.values())
    extras = dict(sistema.contadores)
    extras.update(sistema.alocador.metricas())
    extras["descontinuidades_medias"] = descontinuidades_medias(sistema)
    for codigo, qtd in erros.items():
        extras["erro_" + codigo] = qtd
    return {
        "operacoes": n_ops,
        "erros": sum(erros.values()),
        "acessos_total": camada.acessos,
        "acessos_por_op": camada.acessos / float(n_ops) if n_ops else 0.0,
        "tempo_total_ms": camada.tempo_ms,
        "tempo_medio_op_ms": camada.tempo_ms / float(n_ops) if n_ops else 0.0,
        "max_tabela_global": maximos["tabela_global"],
        "max_tabela_processo": maximos["tabela_processo"],
        "max_soma_tabelas_processo": maximos["soma_processos"],
        "max_contador_aberturas": maximos["contador"],
        "extras": extras,
        "por_operacao": {
            op: {"n": r["n"], "erros": r["erros"], "acessos_medios": r["acessos"] / float(r["n"]),
                 "tempo_medio_ms": r["tempo"] / float(r["n"])}
            for op, r in sorted(por_op.items())
        },
    }
