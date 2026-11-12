#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detector de arquivos suspeitos - esqueleto da atividade "O antivirus por dentro".

A aula e de GESTAO DE ARQUIVOS: vocES vao fazer o sistema de arquivos dizer o que
cada arquivo e (tipo), onde o nome e o conteudo moram, e o que mudou (integridade).

Preencham os seis trechos marcados com TODO. O programa ja roda desde o inicio:
cada etapa que ainda falta aparece como "(TODO)" no relatorio, entao da para
implementar e rodar uma etapa de cada vez.

Requisitos: Python 3.8+ e so a biblioteca padrao. Funciona igual em Windows,
macOS e Linux, nao exige administrador. So LE a pasta de amostras (a etapa 4C
cria e apaga um arquivo de trabalho temporario).

Como rodar:
    python3 detector.py        (no Windows: py detector.py)
"""
import json
import hashlib
import shutil
import tempfile
import os
from datetime import datetime
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
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def ler_bytes(caminho):
    with open(caminho, "rb") as f:
        return f.read()


def listar_arquivos(pasta):
    return sorted(p for p in pasta.iterdir() if p.is_file())


def extensoes_do_tipo(nome_tipo, base):
    for tipo in base["tipos"]:
        if tipo["nome"] == nome_tipo:
            return tipo["extensoes"]
    return None


# ===================================================================
# ETAPA 1 - Identificar o tipo real pelo "magic number"
# O sistema de arquivos sabe o que e um arquivo pelos seus primeiros bytes.
# ===================================================================
def identificar_tipo(dados, base):
    """Compare o INICIO de 'dados' com o magic number de cada tipo da base.
    Converta item["magic_hex"] com bytes.fromhex(...); se dados[:len(magic)]
    == magic, devolva item["nome"]. Se nenhum casar, devolva "desconhecido".
    """
    # TODO etapa 1
    raise NotImplementedError("etapa 1: identificar_tipo")


# ===================================================================
# ETAPA 2 - Varrer o conteudo (os blocos de dados) em busca de assinaturas
# ===================================================================
def varrer_pragas(dados, base):
    """Para cada praga de base["pragas"], converta padrao_hex em bytes e teste
    'if padrao in dados:' (procura em TODO o conteudo). Devolva a lista de nomes.
    """
    # TODO etapa 2
    raise NotImplementedError("etapa 2: varrer_pragas")


# ===================================================================
# ETAPA 3 - O nome (extensao) combina com o conteudo?
# O nome mora no diretorio; o conteudo, nos blocos de dados. Podem divergir.
# ===================================================================
def extensao_coerente(caminho, dados, base):
    """Devolva (coerente, tipo).
    - tipo = identificar_tipo(dados, base)
    - se "desconhecido": devolva (True, tipo)  (nada a cobrar)
    - senao: ext = caminho.suffix.lower().lstrip("."); coerente = ext esta em
      extensoes_do_tipo(tipo, base).
    """
    # TODO etapa 3
    raise NotImplementedError("etapa 3: extensao_coerente")


# ===================================================================
# ETAPA 4A - Hash do conteudo (SHA-256)
# ===================================================================
def sha256_arquivo(caminho):
    """Devolva o SHA-256 do arquivo (hex). Dica: h = hashlib.sha256();
    leia em modo binario ('rb') e alimente h.update(bloco); return h.hexdigest()."""
    # TODO etapa 4A
    raise NotImplementedError("etapa 4A: sha256_arquivo")


# ===================================================================
# ETAPA 4B - Integridade: comparar a pasta com a linha de base
# Percorrer a arvore de arquivos e ver o que mudou.
# ===================================================================
def verificar_integridade(pasta, caminho_linha_de_base):
    """Compare os arquivos de 'pasta' com os hashes de linha["arquivos"].
    Classifique em ok / alterados / ausentes / novos e devolva
    {"ok": [...], "alterados": [...], "ausentes": [...], "novos": [...]}.
    """
    # TODO etapa 4B
    raise NotImplementedError("etapa 4B: verificar_integridade")


# ===================================================================
# ETAPA 4C - Atributos do arquivo (o que o FCB/inode guarda)
# ===================================================================
def atributos(caminho):
    """Leia os atributos que o sistema de arquivos guarda no FCB/inode.
    Devolva (tamanho_em_bytes, data_de_modificacao_em_segundos).
    Dica: st = os.stat(caminho); use st.st_size e st.st_mtime.
    """
    # TODO etapa 4C
    raise NotImplementedError("etapa 4C: atributos")


# ===================================================================
# Demonstracao pronta (usa as etapas 4A e 4C): a data e forjavel, o conteudo nao
# ===================================================================
def _data(segundos):
    return datetime.fromtimestamp(segundos).strftime("%d/%m/%Y %H:%M:%S")


def demonstrar_metadado_vs_conteudo(modelo):
    tmp = Path(tempfile.gettempdir()) / "sisop_trabalho_atributos.dat"
    shutil.copy2(modelo, tmp)
    try:
        tam, data = atributos(tmp)
        h_antes = sha256_arquivo(tmp)
        print("  arquivo de trabalho:", tmp.name)
        print("  antes  -> tamanho: {} bytes | data: {} | hash: {}...".format(tam, _data(data), h_antes[:16]))
        falso = datetime(2000, 1, 1, 0, 0, 0).timestamp()
        os.utime(tmp, (falso, falso))
        tam2, data2 = atributos(tmp)
        h_depois = sha256_arquivo(tmp)
        print("  depois -> tamanho: {} bytes | data: {} (FORJADA) | hash: {}...".format(tam2, _data(data2), h_depois[:16]))
        print("  a data mudou sem tocar no conteudo; o hash continua igual:",
              "SIM" if h_antes == h_depois else "NAO")
        print("  licao: a data vem do FCB/inode e e forjavel; o hash acusa o conteudo.")
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


# ===================================================================
# Relatorio - ja pronto. Mostra "(TODO)" para o que ainda falta.
# ===================================================================
def _tentar(fn, *args, padrao=None):
    try:
        return fn(*args)
    except NotImplementedError:
        return padrao


def principal():
    base = carregar_base()
    print("=" * 66)
    print(" DETECTOR DE ARQUIVOS SUSPEITOS - relatorio")
    print("=" * 66)

    print("\n[ Etapas 1-3 ] O sistema de arquivos identifica cada arquivo\n")
    print("  {:<20} {:<28} {}".format("arquivo", "tipo real (conteudo)", "situacao"))
    print("  " + "-" * 64)
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
        print("  {:<20} {:<28} {}".format(caminho.name, tipo, "  |  ".join(marcas) or "ok"))

    print("\n[ Etapa 4A/4B ] Integridade por conteudo (hash) de", PASTA_SUSPEITA.name + "/\n")
    r = _tentar(verificar_integridade, PASTA_SUSPEITA, LINHA_DE_BASE, padrao=None)
    if r is None:
        print("  (TODO) etapas 4A/4B ainda nao implementadas")
    else:
        print("  integros .......:", ", ".join(r["ok"]) or "(nenhum)")
        print("  ALTERADOS ......:", ", ".join(r["alterados"]) or "(nenhum)")
        print("  AUSENTES .......:", ", ".join(r["ausentes"]) or "(nenhum)")
        print("  INESPERADOS ....:", ", ".join(r["novos"]) or "(nenhum)")

    print("\n[ Etapa 4C ] Atributos do arquivo: a data e forjavel, o conteudo nao\n")
    try:
        demonstrar_metadado_vs_conteudo(PASTA_AMOSTRAS / "leia-me.txt")
    except NotImplementedError:
        print("  (TODO) implemente as etapas 4A e 4C para ver a demonstracao")
    print()


if __name__ == "__main__":
    principal()
