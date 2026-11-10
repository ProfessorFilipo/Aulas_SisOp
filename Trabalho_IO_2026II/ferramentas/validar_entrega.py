# -*- coding: utf-8 -*-
"""
Confere se o trabalho está completo e no formato pedido. FORNECIDO.

Uso (na pasta do repositório do grupo):   python3 ferramentas/validar_entrega.py [pasta] [--json]

Saída: lista de ERROS (corrijam antes de entregar) e AVISOS. Código de saída 1 se houver erro.
Também procura alguns padrões de dados sensíveis (matrícula, CPF, e-mail, chaves e tokens), mas
a responsabilidade de não publicar dados sensíveis é do grupo.
"""
import csv
import io
import json
import os
import re
import sys
import unittest

NUCLEO = ["X1", "X2", "X3", "X4", "X5"]
EXP_DO_MODULO = {"M1": "X6", "M2": "X7", "M3": "X8", "M4": "X9", "M5": "X10", "M6": "X11"}
TESTES_DO_MODULO = {"M1": "TesteM1Cache", "M2": "TesteM2Escalonadores", "M3": "TesteM3DMAeBuffering",
                    "M4": "TesteM4Links", "M5": "TesteM5Protecao", "M6": "TesteM6Alocacao",
                    "integracao": "TesteIntegracao"}
MODULOS_ES, MODULOS_ARQ = {"M1", "M2", "M3"}, {"M4", "M5", "M6"}
SECOES = ["## 0. Resumo", "## 1. Escopo realizado", "## 2. Implementação", "## 3. Experimentos",
          "## 4. Relação com sistemas reais", "## 5. Limitações do simulador", "## 6. Conclusões",
          "## 7. Referências", "## 8. Declaração de autoria e uso de IA"]
CAMPOS = ["Hipótese", "Fundamentação", "Configuração", "Resultados", "Evidências", "Análise", "Veredito"]
VEREDITOS = {"CONFIRMADA", "PARCIALMENTE CONFIRMADA", "REFUTADA"}
GRAFICOS = {"X1": "X1_resposta_media_ms.png", "X2": "X2_cpu.png", "X3": "X3_tempo_por_operacao.png",
            "X4": "X4_open_por_profundidade.png", "X5": "X5_tabelas.png", "X6": "X6_acerto.png",
            "X7": "X7_espera_max_ms.png", "X8": "X8_cpu.png", "X11": "X11_alocacao.png", "X12": "X12_resposta.png"}
URL_REPO = re.compile(r"https?://[\w.-]+/[\w.-]+/[\w.-]+")
SENSIVEIS_ERRO = [
    (re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"), "parece um CPF"),
    (re.compile(r"\b(ghp_|gho_|github_pat_)[A-Za-z0-9_]{20,}"), "parece um token do GitHub"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"), "parece uma chave de API"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "parece uma chave da AWS"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "chave privada"),
]
EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
ARQUIVOS_PROIBIDOS = re.compile(r"(^\.env$|\.pem$|\.key$|^id_rsa)")
MARCADOR = re.compile(r"\[ ?\]|\[ex\.:|^\s*\[[^\]]*\]\s*$|\*\*: \[")
CAMINHO = re.compile(r"\b((?:resultados|graficos)/[\w./\-]+)")


class Achados:
    def __init__(self):
        self.itens = []

    def erro(self, onde, msg):
        self.itens.append(("ERRO", onde, msg))

    def aviso(self, onde, msg):
        self.itens.append(("AVISO", onde, msg))

    def ok(self, onde, msg):
        self.itens.append(("OK", onde, msg))


def exigidos(grupo):
    exps = list(NUCLEO) + [EXP_DO_MODULO[m] for m in grupo.get("modulos", []) if m in EXP_DO_MODULO]
    if grupo.get("integracao"):
        exps.append("X12")
    if grupo.get("bonus_flash"):
        exps.append("X13")
    return exps


def checar_grupo(raiz, a):
    p = os.path.join(raiz, "grupo.json")
    try:
        with open(p, encoding="utf-8") as f:
            g = json.load(f)
    except (OSError, ValueError) as e:
        a.erro("grupo.json", "não foi possível ler: %s" % e)
        return None
    integrantes = g.get("integrantes", [])
    n = len(integrantes)
    if not 1 <= n <= 4:
        a.erro("grupo.json", "o grupo deve ter de 1 a 4 integrantes (há %d)" % n)
    for i in integrantes:
        nome = i.get("nome", "") if isinstance(i, dict) else ""
        if len(nome.split()) < 2 or "Integrante" in nome:
            a.erro("grupo.json", "informem o nome completo de cada integrante: %r" % i)
        if isinstance(i, dict) and set(i) - {"nome"}:
            a.erro("grupo.json", "o repositório é público: deixem só o nome (sem matrícula ou outros dados) em %r" % i)
    repo = g.get("repositorio", "")
    if not URL_REPO.match(repo) or "usuario/nome-do-repositorio" in repo:
        a.erro("grupo.json", "informem o link do repositório público do grupo em \"repositorio\"")
    modulos = g.get("modulos", [])
    desconhecidos = [m for m in modulos if m not in EXP_DO_MODULO]
    if desconhecidos:
        a.erro("grupo.json", "módulos desconhecidos: %s (use M1 a M6)" % desconhecidos)
    m = set(modulos)
    minimo = {1: 0, 2: 1, 3: 2, 4: 3}.get(n, 0)
    if len(m) < minimo:
        a.erro("escopo", "%d integrante(s) exigem pelo menos %d módulo(s); há %d" % (n, minimo, len(m)))
    if n >= 3 and (not m & MODULOS_ES or not m & MODULOS_ARQ):
        a.erro("escopo", "com %d integrantes, escolham ao menos um módulo de E/S (M1–M3) e um de arquivos (M4–M6)" % n)
    if n == 4 and not g.get("integracao"):
        a.erro("escopo", "grupos de 4 integrantes devem fazer a integração (\"integracao\": true)")
    a.ok("grupo.json", "%d integrante(s), módulos %s, integração %s" % (n, sorted(m) or "nenhum",
                                                                       "sim" if g.get("integracao") else "não"))
    return g


def checar_testes(raiz, g, a):
    sys.path.insert(0, raiz)
    saida = io.StringIO()
    try:
        suite = unittest.defaultTestLoader.discover(os.path.join(raiz, "testes"), top_level_dir=raiz)
        res = unittest.TextTestRunner(stream=saida, verbosity=0).run(suite)
    except Exception as e:
        a.erro("testes", "não foi possível rodar os testes: %s" % e)
        return
    falhas = [t.id() for t, _ in res.failures + res.errors]
    pulados = [t.id() for t, _ in res.skipped]
    nucleo = [f for f in falhas if ".test_nucleo." in f or ".test_fornecido." in f]
    if nucleo:
        a.erro("testes", "%d teste(s) do núcleo falhando: %s" % (len(nucleo), ", ".join(x.split(".")[-1] for x in nucleo)))
    escolhidos = list(g.get("modulos", [])) + (["integracao"] if g.get("integracao") else [])
    for mod in escolhidos:
        classe = TESTES_DO_MODULO.get(mod)
        if not classe:
            continue
        ruins = [t for t in falhas + pulados if ".%s." % classe in t]
        if ruins:
            a.erro("testes", "%s: testes falhando ou não implementados: %s" % (mod, ", ".join(x.split(".")[-1] for x in ruins)))
    if not nucleo:
        a.ok("testes", "%d testes executados, %d falhas, %d pulados" % (res.testsRun, len(falhas), len(pulados)))


def checar_resultados(raiz, g, a):
    p = os.path.join(raiz, "resultados", "experimentos.csv")
    if not os.path.exists(p):
        a.erro("resultados/", "não encontrado: rodem  python3 executar.py experimentos")
        return
    with open(p, encoding="utf-8") as f:
        status = {r["experimento"]: r for r in csv.DictReader(f)}
    for exp in exigidos(g):
        r = status.get(exp)
        if not r or r["status"] != "ok":
            a.erro("resultados/", "%s não está ok (%s)" % (exp, r["status"] if r else "ausente"))
    try:
        sys.path.insert(0, raiz)
        from simes.metricas import COLUNAS
        for arquivo, colunas in COLUNAS.items():
            caminho = os.path.join(raiz, "resultados", arquivo)
            if os.path.exists(caminho):
                with open(caminho, encoding="utf-8") as f:
                    cab = next(csv.reader(f), [])
                if cab != colunas:
                    a.erro("resultados/" + arquivo, "cabeçalho diferente do gerado pelo simulador")
    except ImportError:
        pass
    for exp in exigidos(g):
        if exp in GRAFICOS and not os.path.exists(os.path.join(raiz, "graficos", GRAFICOS[exp])):
            a.aviso("graficos/", "falta %s (rodem  python3 graficos.py, ou incluam o gráfico equivalente)" % GRAFICOS[exp])
    a.ok("resultados/", "experimentos exigidos: %s" % ", ".join(exigidos(g)))


def checar_relatorio(raiz, g, a):
    p = os.path.join(raiz, "RELATORIO.md")
    if not os.path.exists(p):
        a.erro("RELATORIO.md", "não encontrado")
        return
    with open(p, encoding="utf-8") as f:
        texto = f.read()
    m = re.search(r"^\*\*Integrantes:\*\*[ \t]*(.*)$", texto, re.M)
    if not m or not m.group(1).strip() or MARCADOR.search(m.group(1)):
        a.erro("RELATORIO.md", "a linha **Integrantes:** deve trazer o nome completo de todos os integrantes")
    else:
        for i in g.get("integrantes", []):
            nome = i.get("nome", "") if isinstance(i, dict) else ""
            if nome and nome.lower() not in m.group(1).lower():
                a.erro("RELATORIO.md", "integrante de grupo.json ausente na linha **Integrantes:**: %s" % nome)
    m = re.search(r"^\*\*Repositório:\*\*[ \t]*(.*)$", texto, re.M)
    if not m or not URL_REPO.search(m.group(1)) or "usuario/repositorio" in m.group(1):
        a.erro("RELATORIO.md", "a linha **Repositório:** deve trazer o link do repositório público do grupo")
    elif g.get("repositorio") and g["repositorio"].rstrip("/") not in m.group(1):
        a.aviso("RELATORIO.md", "o link do relatório difere do informado em grupo.json")
    if "INSTRUÇÕES DO MODELO" in texto:
        a.aviso("RELATORIO.md", "apaguem o bloco de instruções do modelo")
    for s in SECOES:
        if not re.search(r"^" + re.escape(s) + r"\s*$", texto, re.M):
            a.erro("RELATORIO.md", "seção ausente ou renomeada: '%s'" % s)
    secoes = {m.group(1): m.start() for m in re.finditer(r"^### (X\d{1,2}) — .+$", texto, re.M)}
    for exp in exigidos(g):
        if exp not in secoes:
            a.erro("RELATORIO.md", "falta a seção '### %s — ...'" % exp)
            continue
        ini = secoes[exp]
        prox = re.search(r"^#{2,3} ", texto[ini + 4:], re.M)
        bloco = texto[ini:ini + 4 + prox.start()] if prox else texto[ini:]
        for campo in CAMPOS:
            m = re.search(r"^\*\*%s:\*\*[ \t]*(.*)$" % campo, bloco, re.M)
            if not m:
                a.erro("RELATORIO.md §%s" % exp, "campo **%s:** ausente" % campo)
                continue
            conteudo = re.split(r"\n\s*\n(?=\*\*|#)", bloco[m.start():], maxsplit=1)[0].split(":**", 1)[1].strip()
            if not conteudo or MARCADOR.search(conteudo):
                a.erro("RELATORIO.md §%s" % exp, "campo **%s:** não preenchido" % campo)
            elif campo == "Veredito" and conteudo.strip(" .").upper() not in VEREDITOS:
                a.erro("RELATORIO.md §%s" % exp, "veredito inválido: %s" % conteudo)
            elif campo == "Evidências":
                caminhos = CAMINHO.findall(conteudo)
                if not caminhos:
                    a.erro("RELATORIO.md §%s" % exp, "Evidências sem caminho de arquivo (resultados/... ou graficos/...)")
                for c in caminhos:
                    if not os.path.exists(os.path.join(raiz, c.rstrip(".;,)"))):
                        a.erro("RELATORIO.md §%s" % exp, "arquivo citado não existe: %s" % c)
    for exp in secoes:
        if exp not in exigidos(g):
            a.aviso("RELATORIO.md", "a seção %s não faz parte do escopo declarado em grupo.json" % exp)
    restantes = [l for l in texto.splitlines() if MARCADOR.search(l)]
    if restantes:
        a.aviso("RELATORIO.md", "%d linha(s) ainda com texto do modelo entre colchetes, ex.: %s"
                % (len(restantes), restantes[0].strip()[:70]))
    a.ok("RELATORIO.md", "%d seção(ões) de experimento" % len(secoes))


def checar_pasta(raiz, a):
    """Arquivos grandes e padrões de dados sensíveis (o repositório é público)."""
    achou = False
    for dirpath, dirs, arqs in os.walk(raiz):
        for ignorar in ("__pycache__", ".git", "cargas", "resultados", "graficos", ".venv", "venv"):
            if ignorar in dirs:
                dirs.remove(ignorar)
        for nome in arqs:
            c = os.path.join(dirpath, nome)
            rel = os.path.relpath(c, raiz)
            if os.path.getsize(c) > 20 * 2 ** 20:
                a.aviso(rel, "arquivo com mais de 20 MiB")
            if ARQUIVOS_PROIBIDOS.search(nome):
                a.erro(rel, "arquivo que costuma conter segredos: não pode ir para o repositório público")
                achou = True
                continue
            if not nome.endswith((".py", ".md", ".json", ".txt", ".csv", ".cfg", ".ini", ".yml", ".yaml", ".toml")):
                continue
            try:
                with open(c, encoding="utf-8") as f:
                    texto = f.read()
            except (UnicodeDecodeError, OSError):
                continue
            for padrao, descricao in SENSIVEIS_ERRO:
                if padrao.search(texto):
                    a.erro(rel, "possível dado sensível: %s" % descricao)
                    achou = True
            emails = [e for e in EMAIL.findall(texto) if not e.endswith(("example.com", "exemplo.com"))]
            if emails:
                a.aviso(rel, "contém e-mail (%s): o repositório é público, confiram se pode ficar" % emails[0])
                achou = True
            if nome in ("grupo.json", "RELATORIO.md") and re.search(r"\b\d{8,9}\b", texto):
                a.aviso(rel, "contém número que parece matrícula: não publiquem matrículas")
                achou = True
    if not achou:
        a.ok("dados sensíveis", "nenhum padrão suspeito encontrado (a conferência final é do grupo)")


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    raiz = os.path.abspath(args[0] if args else os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    a = Achados()
    g = checar_grupo(raiz, a)
    if g is not None:
        checar_testes(raiz, g, a)
        checar_resultados(raiz, g, a)
        checar_relatorio(raiz, g, a)
    checar_pasta(raiz, a)
    if "--json" in sys.argv:
        print(json.dumps([{"nivel": n, "onde": o, "mensagem": m} for n, o, m in a.itens], ensure_ascii=False, indent=2))
    else:
        for nivel, onde, msg in a.itens:
            print("[%-5s] %-26s %s" % (nivel, onde, msg))
        ne = sum(1 for i in a.itens if i[0] == "ERRO")
        na = sum(1 for i in a.itens if i[0] == "AVISO")
        print("\nResultado: %d erro(s), %d aviso(s). %s" % (ne, na, "Entrega pronta." if ne == 0 else "Corrijam os erros antes de entregar."))
    sys.exit(1 if any(i[0] == "ERRO" for i in a.itens) else 0)


if __name__ == "__main__":
    main()
