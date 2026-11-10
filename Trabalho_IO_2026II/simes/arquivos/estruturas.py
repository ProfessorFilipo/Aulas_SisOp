# -*- coding: utf-8 -*-
"""
Estruturas de dados do sistema de arquivos. FORNECIDO.

Referência: Silberschatz, 9ª ed., cap. 11 (FCB, tabelas de arquivos abertos, diretórios).
"""


class ErroSA(Exception):
    """
    Erro de uma operação do sistema de arquivos. Use os códigos POSIX:
    ENOENT (não existe), EEXIST (já existe), ENOTDIR (não é diretório), EISDIR (é diretório),
    EBADF (descritor inválido ou modo incompatível), EINVAL (argumento inválido),
    ENOSPC (sem espaço), EACCES (permissão negada), EPERM (operação não permitida),
    EBUSY (arquivo travado por outro processo), ELOOP (links simbólicos demais).
    """

    def __init__(self, codigo, detalhe=""):
        super().__init__("%s %s" % (codigo, detalhe))
        self.codigo = codigo


class FCB:
    """
    File Control Block: os metadados de um arquivo, diretório ou link simbólico.

    tipo        'arquivo' | 'diretorio' | 'simbolico'
    tamanho     em bytes (arquivos)
    blocos      blocos físicos de DADOS, na ordem lógica (definidos pelo alocador)
    pai         id do FCB do diretório onde o arquivo foi criado
    links       número de entradas de diretório que apontam para este FCB (hard links)
    entradas    só diretórios: dict nome -> id do FCB
    alvo        só links simbólicos: caminho absoluto do alvo
    dono, permissoes, acl   proteção (M5); acl = lista de (usuario, 'rwx')
    sujo        True se os metadados mudaram desde o último close (tamanho, datas)
    extra       dict livre para o alocador (ex.: blocos de índice)
    """

    def __init__(self, id, nome, tipo, pai, agora_ms=0.0, dono="root"):
        self.id = id
        self.nome = nome
        self.tipo = tipo
        self.pai = pai
        self.tamanho = 0
        self.blocos = []
        self.links = 1
        self.entradas = {} if tipo == "diretorio" else None
        self.alvo = None
        self.dono = dono
        self.permissoes = 0o755 if tipo == "diretorio" else 0o644
        self.acl = []
        self.criado_ms = agora_ms
        self.modificado_ms = agora_ms
        self.sujo = False
        self.extra = {}

    def __repr__(self):
        return "FCB(%d %s %s tam=%d blocos=%d links=%d)" % (self.id, self.tipo, self.nome,
                                                           self.tamanho, len(self.blocos), self.links)


class EntradaGlobal:
    """Uma entrada por ARQUIVO aberto (por qualquer processo)."""

    def __init__(self, fcb_id):
        self.fcb_id = fcb_id
        self.contador = 0          # quantas aberturas (de qualquer processo) apontam para cá
        self.trava = None          # M5: processo que detém a trava exclusiva, ou None


class EntradaProcesso:
    """Uma entrada por ABERTURA, na tabela do processo que abriu."""

    def __init__(self, fcb_id, modo, posicao=0):
        self.fcb_id = fcb_id       # chave da entrada global correspondente
        self.modo = modo           # 'r', 'w', 'rw' ou 'a'
        self.posicao = posicao     # ponteiro de posição, em bytes
