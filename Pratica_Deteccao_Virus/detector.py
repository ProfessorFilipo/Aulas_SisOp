#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detector de arquivos suspeitos - esqueleto da atividade "O antivirus por dentro".

Preencham os cinco trechos marcados com TODO. O programa ja roda desde o inicio:
cada etapa que voces ainda nao implementaram aparece como "(TODO)" no relatorio,
entao da para implementar e rodar uma etapa de cada vez.

Requisitos: Python 3.8+ e so a biblioteca padrao. Funciona igual em Windows,
macOS e Linux, nao exige administrador e so LE arquivos da pasta de amostras.

Como rodar:
    python3 detector.py        (no Windows: py detector.py)
"""
import json
import hashlib
from pathlib import Path

BASE = Path(__file__).resolve().parent
ARQ_BASE = BASE / "base_assinaturas.json"
PASTA_AMOSTRAS = BASE / "amostras"
PASTA_SUSPEITA = BASE / "instalacao_depois"
LINHA_DE_BASE = BASE / "linha_de_base.json"


# ===================================================================
# Utilidades ja prontas - nao precisam mexer
# ===================================================================
def carregar_base(caminho=ARQ_BASE):
    """Le a base de assinaturas (JSON) e devolve o dicionario."""
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def ler_bytes(caminho):
    """Le o arquivo inteiro em modo binario e devolve os bytes."""
    with open(caminho, "rb") as f:
        return f.read()


def listar_arquivos(pasta):
    """Lista os arquivos de uma pasta em ordem alfabetica estavel entre SOs."""
    return sorted(p for p in pasta.iterdir() if p.is_file())


def extensoes_do_tipo(nome_tipo, base):
    """Devolve a lista de extensoes aceitas para um tipo da base."""
    for tipo in base["tipos"]:
        if tipo["nome"] == nome_tipo:
            return tipo["extensoes"]
    return None


# ===================================================================
# ETAPA 1 - Identificar o tipo real pelo "magic number"
# ===================================================================
def identificar_tipo(dados, base):
    """Compare o INICIO de 'dados' com o magic number de cada tipo da base.

    Para cada item de base["tipos"]:
      - converta item["magic_hex"] em bytes com  bytes.fromhex(...)
      - se  dados[:len(magic)] == magic , esse e o tipo: devolva item["nome"]
    Se nenhum casar, devolva "desconhecido".
    """
    # TODO etapa 1
    raise NotImplementedError("etapa 1: identificar_tipo")


# ===================================================================
# ETAPA 2 - Varrer o conteudo em busca de assinaturas de praga
# ===================================================================
def varrer_pragas(dados, base):
    """Procure cada assinatura de base["pragas"] em QUALQUER posicao de 'dados'.

    Para cada praga:
      - converta praga["padrao_hex"] em bytes com  bytes.fromhex(...)
      - teste  if padrao in dados:   (o operador 'in' procura em todo o conteudo)
    Devolva a lista com os nomes (praga["nome"]) das assinaturas encontradas.
    """
    # TODO etapa 2
    raise NotImplementedError("etapa 2: varrer_pragas")


# ===================================================================
# ETAPA 3 - A extensao combina com o conteudo?
# ===================================================================
def extensao_coerente(caminho, dados, base):
    """Devolva (coerente, tipo).

    - Descubra o tipo com identificar_tipo(dados, base).
    - Se o tipo for "desconhecido", nao ha o que cobrar: devolva (True, tipo).
    - Senao, pegue a extensao do arquivo:  caminho.suffix.lower().lstrip(".")
      e as extensoes aceitas com  extensoes_do_tipo(tipo, base).
      'coerente' e True se a extensao estiver na lista de aceitas.
    """
    # TODO etapa 3
    raise NotImplementedError("etapa 3: extensao_coerente")


# ===================================================================
# ETAPA 4 - Integridade por hash (SHA-256)
# ===================================================================
def sha256_arquivo(caminho):
    """Calcule e devolva o SHA-256 do arquivo, em hexadecimal.

    Dica: h = hashlib.sha256(); leia o arquivo em modo binario ('rb') e
    chame h.update(bloco) para cada pedaco lido; devolva h.hexdigest().
    """
    # TODO etapa 4 (parte A)
    raise NotImplementedError("etapa 4A: sha256_arquivo")


def verificar_integridade(pasta, caminho_linha_de_base):
    """Compare os arquivos de 'pasta' com a linha de base de hashes.

    - Carregue o JSON da linha de base; os hashes estao em linha["arquivos"]
      (dicionario nome -> hash esperado).
    - Calcule o hash atual de cada arquivo de 'pasta' (use listar_arquivos e
      sha256_arquivo); use p.name como chave.
    - Classifique:
        ok ........ esta na base e o hash bate
        alterados . esta na base mas o hash mudou
        ausentes .. esta na base e sumiu da pasta
        novos ..... esta na pasta mas nao estava na base
    Devolva {"ok": [...], "alterados": [...], "ausentes": [...], "novos": [...]}.
    """
    # TODO etapa 4 (parte B)
    raise NotImplementedError("etapa 4B: verificar_integridade")


# ===================================================================
# Relatorio - ja pronto. Mostra "(TODO)" para o que ainda falta.
# ===================================================================
def _tentar(fn, *args, padrao=None):
    """Chama fn(*args); se ainda for um TODO, devolve 'padrao'."""
    try:
        return fn(*args)
    except NotImplementedError:
        return padrao


def principal():
    base = carregar_base()
    print("=" * 64)
    print(" DETECTOR DE ARQUIVOS SUSPEITOS - relatorio")
    print("=" * 64)

    print("\n[ Etapas 1-3 ] Varredura de", PASTA_AMOSTRAS.name + "/\n")
    print("  {:<20} {:<28} {}".format("arquivo", "tipo real", "situacao"))
    print("  " + "-" * 62)
    for caminho in listar_arquivos(PASTA_AMOSTRAS):
        dados = ler_bytes(caminho)
        tipo = _tentar(identificar_tipo, dados, base, padrao="(TODO)")
        pragas = _tentar(varrer_pragas, dados, base, padrao=None)
        par = _tentar(extensao_coerente, caminho, dados, base, padrao=None)

        marcas = []
        if pragas:
            marcas.append("ASSINATURA: " + ", ".join(pragas))
        if par is not None and par[0] is False:
            marcas.append("EXTENSAO NAO BATE COM O CONTEUDO")
        situacao = "  |  ".join(marcas) if marcas else "ok"
        print("  {:<20} {:<28} {}".format(caminho.name, tipo, situacao))

    print("\n[ Etapa 4 ] Integridade de", PASTA_SUSPEITA.name + "/ contra a linha de base\n")
    r = _tentar(verificar_integridade, PASTA_SUSPEITA, LINHA_DE_BASE, padrao=None)
    if r is None:
        print("  (TODO) etapa 4 ainda nao implementada")
    else:
        print("  integros .......:", ", ".join(r["ok"]) or "(nenhum)")
        print("  ALTERADOS ......:", ", ".join(r["alterados"]) or "(nenhum)")
        print("  AUSENTES .......:", ", ".join(r["ausentes"]) or "(nenhum)")
        print("  INESPERADOS ....:", ", ".join(r["novos"]) or "(nenhum)")
    print()


if __name__ == "__main__":
    principal()
