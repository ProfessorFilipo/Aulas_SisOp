# -*- coding: utf-8 -*-
"""
validar_entrega.py - confere a estrutura da entrega do trabalho pratico
Sistemas Operacionais - PUCRS - Prof. Filipo Novo Mor

Uso:  python3 validar_entrega.py <pasta_da_entrega> [--json]
Saida: lista de ERROS (impedem a avaliacao completa) e AVISOS. Codigo de saida 1 se houver erro.
Somente biblioteca padrao.
"""
import csv
import json
import os
import re
import sys
from collections import defaultdict

IDS = ["A1", "A2", "A3", "A4", "A5", "A6", "B"] + ["C%d" % i for i in range(1, 13)]
ESCOPO = {
    1: {"ids": ["A1", "A3", "A4"] + ["C%d" % i for i in range(1, 9)], "sistemas": 1, "sfs_por_sistema": 1},
    2: {"ids": ["A1", "A2", "A3", "A4", "A5"] + ["C%d" % i for i in range(1, 13)], "sistemas": 1, "sfs_por_sistema": 2},
    3: {"ids": ["A1", "A2", "A3", "A4", "A5", "B"] + ["C%d" % i for i in range(1, 13)], "sistemas": 2, "sfs_por_sistema": 1},
    4: {"ids": IDS, "sistemas": 2, "sfs_por_sistema": 2},
}
SECOES = ["## 0. Resumo", "## 1. Ambiente de testes", "## 2. Metodologia comum", "## 3. Experimentos",
          "## 4. Análise cruzada entre sistemas", "## 5. Ameaças à validade", "## 6. Conclusões",
          "## 7. Referências", "## 8. Declaração de autoria e uso de ferramentas"]
CAMPOS = ["Hipótese", "Fundamentação", "Procedimento", "Resultados", "Evidências", "Análise", "Veredito"]
VEREDITOS = {"CONFIRMADA", "PARCIALMENTE CONFIRMADA", "REFUTADA"}

CSVS = {
    "A_desempenho.csv": {
        "colunas": ["experimento", "sistema", "sf", "operacao", "padrao_acesso", "tamanho_bloco_bytes",
                    "tamanho_total_bytes", "estado_cache", "modo_durabilidade", "modo_es", "repeticao",
                    "tempo_s", "vazao_mib_s", "operacoes_por_s", "cpu_usuario_s", "cpu_sistema_s",
                    "interrupcoes_disco", "log"],
        "valores": {"experimento": {"A1", "A2", "A3", "A4", "A5", "A6"},
                    "operacao": {"leitura", "escrita"},
                    "padrao_acesso": {"sequencial", "aleatorio"},
                    "estado_cache": {"frio", "quente", "nao_se_aplica"},
                    "modo_durabilidade": {"nenhum", "fsync_final", "fsync_cada", "o_sync", "o_dsync",
                                          "write_through", "full_fsync", "nao_se_aplica"},
                    "modo_es": {"bufferizada", "direta"}},
        "numericas": ["tamanho_bloco_bytes", "tamanho_total_bytes", "repeticao", "tempo_s", "vazao_mib_s",
                      "operacoes_por_s", "cpu_usuario_s", "cpu_sistema_s", "interrupcoes_disco"],
        "obrigatorias": ["tempo_s", "repeticao"],
        "config": ["experimento", "sistema", "sf", "operacao", "padrao_acesso", "tamanho_bloco_bytes",
                   "tamanho_total_bytes", "estado_cache", "modo_durabilidade", "modo_es"],
    },
    "B_modelos_es.csv": {
        "colunas": ["experimento", "sistema", "modelo", "mecanismo", "n_clientes_lentos", "repeticao", "duracao_s",
                    "latencia_sonda_media_ms", "latencia_sonda_p95_ms", "vazao_total_kib_s", "cpu_usuario_s",
                    "cpu_sistema_s", "threads_max", "descritores_max", "falhou", "motivo_falha", "log"],
        "valores": {"experimento": {"B0", "B1", "B2", "B3", "B4"},
                    "modelo": {"sequencial_bloqueante", "thread_por_cliente", "nao_bloqueante_polling",
                               "multiplexado", "assincrono"},
                    "falhou": {"sim", "nao"}},
        "numericas": ["n_clientes_lentos", "repeticao", "duracao_s", "latencia_sonda_media_ms",
                      "latencia_sonda_p95_ms", "vazao_total_kib_s", "cpu_usuario_s", "cpu_sistema_s",
                      "threads_max", "descritores_max"],
        "obrigatorias": ["n_clientes_lentos", "repeticao"],
        "config": ["experimento", "sistema", "modelo", "mecanismo", "n_clientes_lentos"],
    },
    "C_conformidade.csv": {
        "colunas": ["teste", "sistema", "sf", "caso", "hipotese", "observado", "codigo_erro",
                    "confirmou_hipotese", "log"],
        "valores": {"teste": {"C%d" % i for i in range(1, 13)}, "confirmou_hipotese": {"sim", "nao"}},
        "numericas": [],
        "obrigatorias": ["caso", "hipotese", "observado"],
        "config": None,
    },
}
MIN_REPETICOES = 5
PLACEHOLDER = re.compile(r"\[ ?\]|\[ex\.:|^\s*\[[^\]]*\]\s*$|\*\*: \[")
CAMINHO = re.compile(r"\b((?:logs|resultados|graficos|ambiente|codigo)/[\w./\-]+)")


class Relatorio:
    def __init__(self):
        self.itens = []

    def erro(self, onde, msg):
        self.itens.append(("ERRO", onde, msg))

    def aviso(self, onde, msg):
        self.itens.append(("AVISO", onde, msg))

    def ok(self, onde, msg):
        self.itens.append(("OK", onde, msg))


def carregar_grupo(raiz, r):
    p = os.path.join(raiz, "grupo.json")
    if not os.path.exists(p):
        r.erro("grupo.json", "arquivo não encontrado")
        return None
    try:
        with open(p, encoding="utf-8") as f:
            g = json.load(f)
    except ValueError as e:
        r.erro("grupo.json", "JSON inválido: %s" % e)
        return None
    n = len(g.get("integrantes", []))
    if not 1 <= n <= 4:
        r.erro("grupo.json", "o grupo deve ter de 1 a 4 integrantes (encontrados %d)" % n)
    for i in g.get("integrantes", []):
        if not i.get("nome") or "Integrante" in i.get("nome", "") or not i.get("matricula") or set(i.get("matricula", "")) == {"0"}:
            r.erro("grupo.json", "integrante sem nome ou matrícula preenchidos: %r" % i)
    sistemas = {s.get("id") for s in g.get("sistemas", [])}
    sfs = {f.get("id"): f.get("sistema") for f in g.get("sistemas_de_arquivos", [])}
    for fid, sid in sfs.items():
        if sid not in sistemas:
            r.erro("grupo.json", "sistema de arquivos %s aponta para sistema inexistente %s" % (fid, sid))
    partes = g.get("partes_realizadas", [])
    for x in partes:
        if x not in IDS:
            r.erro("grupo.json", "ID de experimento desconhecido em partes_realizadas: %s" % x)
    if 1 <= n <= 4:
        esc = ESCOPO[n]
        faltam = [x for x in esc["ids"] if x not in partes]
        if faltam:
            r.erro("escopo", "para %d integrante(s) faltam os experimentos: %s" % (n, ", ".join(faltam)))
        if len(sistemas) < esc["sistemas"]:
            r.erro("escopo", "para %d integrante(s) são exigidos %d sistema(s) operacional(is); há %d"
                   % (n, esc["sistemas"], len(sistemas)))
        por_sis = defaultdict(int)
        for fid, sid in sfs.items():
            por_sis[sid] += 1
        for sid in sistemas:
            if por_sis[sid] < esc["sfs_por_sistema"]:
                r.erro("escopo", "o sistema %s precisa de %d sistema(s) de arquivos; há %d"
                       % (sid, esc["sfs_por_sistema"], por_sis[sid]))
    g["_sistemas"], g["_sfs"], g["_n"] = sistemas, set(sfs), n
    r.ok("grupo.json", "%d integrante(s), %d sistema(s), %d sistema(s) de arquivos, %d experimento(s)"
         % (n, len(sistemas), len(sfs), len(partes)))
    return g


def checar_csv(raiz, nome, spec, g, r):
    p = os.path.join(raiz, "resultados", nome)
    parte = nome[0]
    ids_parte = [x for x in g.get("partes_realizadas", []) if x.startswith(parte)]
    if not os.path.exists(p):
        if ids_parte:
            r.erro("resultados/" + nome, "arquivo não encontrado")
        return
    with open(p, encoding="utf-8-sig", newline="") as f:
        leitor = csv.reader(f)
        try:
            cab = next(leitor)
        except StopIteration:
            r.erro("resultados/" + nome, "arquivo vazio (falta até o cabeçalho)")
            return
        linhas = list(leitor)
    cab = [c.strip() for c in cab]
    if cab != spec["colunas"]:
        r.erro("resultados/" + nome, "cabeçalho diferente do modelo. Esperado: %s" % ",".join(spec["colunas"]))
        return
    if not ids_parte:
        if linhas:
            r.aviso("resultados/" + nome, "há dados, mas nenhum experimento desta parte em partes_realizadas")
        return
    if not linhas:
        r.erro("resultados/" + nome, "sem linhas de dados")
        return
    erros = 0
    vistos = set()
    grupos = defaultdict(set)
    for n, l in enumerate(linhas, start=2):
        if not any(c.strip() for c in l):
            continue
        if len(l) != len(cab):
            r.erro("resultados/%s:%d" % (nome, n), "número de colunas errado (%d)" % len(l))
            erros += 1
            continue
        d = dict(zip(cab, (c.strip() for c in l)))
        chave_id = d.get("experimento") or d.get("teste")
        vistos.add(chave_id if parte != "B" else "B")
        for col, permitidos in spec["valores"].items():
            if d[col] not in permitidos:
                r.erro("resultados/%s:%d" % (nome, n), "valor '%s' inválido em %s (permitidos: %s)"
                       % (d[col], col, ", ".join(sorted(permitidos))))
                erros += 1
        if d["sistema"] not in g["_sistemas"]:
            r.erro("resultados/%s:%d" % (nome, n), "sistema '%s' não existe em grupo.json" % d["sistema"])
            erros += 1
        if "sf" in d and d["sf"] not in g["_sfs"]:
            r.erro("resultados/%s:%d" % (nome, n), "sf '%s' não existe em grupo.json" % d["sf"])
            erros += 1
        falhou = d.get("falhou") == "sim"
        for col in spec["numericas"]:
            if d[col] == "":
                if col in spec["obrigatorias"] or (parte == "B" and not falhou and col == "latencia_sonda_media_ms"):
                    r.erro("resultados/%s:%d" % (nome, n), "coluna %s vazia" % col)
                    erros += 1
                continue
            try:
                float(d[col].replace(",", "."))
                if "," in d[col]:
                    r.aviso("resultados/%s:%d" % (nome, n), "use ponto como separador decimal em %s" % col)
            except ValueError:
                r.erro("resultados/%s:%d" % (nome, n), "valor não numérico em %s: '%s'" % (col, d[col]))
                erros += 1
        for col in spec["obrigatorias"]:
            if col not in spec["numericas"] and not d[col]:
                r.erro("resultados/%s:%d" % (nome, n), "coluna %s vazia" % col)
                erros += 1
        if d.get("log"):
            if not os.path.exists(os.path.join(raiz, d["log"])):
                r.erro("resultados/%s:%d" % (nome, n), "log citado não existe: %s" % d["log"])
                erros += 1
        else:
            r.aviso("resultados/%s:%d" % (nome, n), "coluna log vazia")
        if spec["config"] and not falhou:
            grupos[tuple(d[c] for c in spec["config"])].add(d["repeticao"])
    for x in ids_parte:
        if x not in vistos:
            r.erro("resultados/" + nome, "nenhuma linha para o experimento %s" % x)
    poucas = [k for k, reps in grupos.items() if len(reps) < MIN_REPETICOES]
    for k in poucas[:10]:
        r.erro("resultados/" + nome, "menos de %d repetições na configuração %s"
               % (MIN_REPETICOES, dict(zip(spec["config"], k))))
    if len(poucas) > 10:
        r.erro("resultados/" + nome, "... e mais %d configurações com poucas repetições" % (len(poucas) - 10))
    if not erros and not poucas:
        r.ok("resultados/" + nome, "%d linhas válidas" % len(linhas))


def checar_relatorio(raiz, g, r):
    p = os.path.join(raiz, "RELATORIO.md")
    if not os.path.exists(p):
        r.erro("RELATORIO.md", "arquivo não encontrado")
        return
    with open(p, encoding="utf-8") as f:
        texto = f.read()
    if "INSTRUÇÕES DO MODELO" in texto:
        r.aviso("RELATORIO.md", "apague o bloco de instruções do modelo")
    for s in SECOES:
        if not re.search(r"^" + re.escape(s) + r"\s*$", texto, re.M):
            r.erro("RELATORIO.md", "seção obrigatória ausente ou renomeada: '%s'" % s)
    partes = g.get("partes_realizadas", [])
    secoes_exp = {m.group(1): m.start() for m in re.finditer(r"^### (A\d|B|C\d{1,2}) — .+$", texto, re.M)}
    for x in secoes_exp:
        if x not in partes:
            r.aviso("RELATORIO.md", "seção ### %s existe, mas %s não está em partes_realizadas (apague ou inclua)" % (x, x))
    posicoes = sorted(secoes_exp.values()) + [len(texto)]
    for x in partes:
        if x not in secoes_exp:
            r.erro("RELATORIO.md", "falta a seção '### %s — ...'" % x)
            continue
        ini = secoes_exp[x]
        fim = min(pos for pos in posicoes if pos > ini)
        prox = re.search(r"^#{2,3} ", texto[ini + 4:fim], re.M)
        bloco = texto[ini:ini + 4 + prox.start()] if prox else texto[ini:fim]
        for campo in CAMPOS:
            m = re.search(r"^\*\*%s:\*\*[ \t]*(.*)$" % campo, bloco, re.M)
            if not m:
                r.erro("RELATORIO.md §%s" % x, "campo **%s:** ausente" % campo)
                continue
            resto = re.split(r"\n\s*\n(?=\*\*|#)", bloco[m.start():], maxsplit=1)[0]
            conteudo = resto.split(":**", 1)[1].strip()
            if not conteudo or PLACEHOLDER.search(conteudo):
                r.erro("RELATORIO.md §%s" % x, "campo **%s:** não preenchido" % campo)
            elif campo == "Veredito" and conteudo.strip(" .").upper() not in VEREDITOS:
                r.erro("RELATORIO.md §%s" % x, "veredito '%s' inválido (use: %s)" % (conteudo, ", ".join(sorted(VEREDITOS))))
            elif campo == "Evidências":
                caminhos = CAMINHO.findall(conteudo)
                if not caminhos:
                    r.erro("RELATORIO.md §%s" % x, "Evidências sem caminho de arquivo (logs/..., resultados/..., graficos/...)")
                for c in caminhos:
                    c = c.rstrip(".;,)")
                    if not os.path.exists(os.path.join(raiz, c)):
                        r.erro("RELATORIO.md §%s" % x, "evidência citada não existe: %s" % c)
    resto_ph = [l for l in texto.splitlines() if PLACEHOLDER.search(l)]
    if resto_ph:
        r.aviso("RELATORIO.md", "%d linha(s) ainda com texto de modelo entre colchetes, ex.: %s"
                % (len(resto_ph), resto_ph[0].strip()[:70]))
    if g.get("_n") == 4:
        m = re.search(r"^## 4\. .*?$(.*?)^## 5\.", texto, re.M | re.S)
        if not m or len(m.group(1).split()) < 150:
            r.erro("RELATORIO.md §4", "grupos de 4 integrantes devem fazer a análise cruzada (mínimo de 150 palavras)")
    r.ok("RELATORIO.md", "%d seção(ões) de experimento encontradas" % len(secoes_exp))


def checar_pastas(raiz, g, r):
    for sid in sorted(g["_sistemas"]):
        if not os.path.exists(os.path.join(raiz, "ambiente", "ambiente_%s.json" % sid)):
            r.erro("ambiente/", "falta ambiente_%s.json (gere com coletar_ambiente.py)" % sid)
    logs = [f for f in os.listdir(os.path.join(raiz, "logs"))] if os.path.isdir(os.path.join(raiz, "logs")) else []
    if not [f for f in logs if f.endswith((".log", ".txt")) and f != "LEIA-ME.txt"]:
        r.erro("logs/", "nenhum log de execução encontrado")
    cod = os.path.join(raiz, "codigo")
    if not os.path.isdir(cod) or not [f for f in os.listdir(cod) if f.lower().startswith("executar_tudo")]:
        r.erro("codigo/", "falta o script executar_tudo (.sh, .ps1 ou .py)")
    for pasta in ("ambiente", "codigo", "logs", "graficos"):
        if os.path.exists(os.path.join(raiz, pasta, "LEIA-ME.txt")):
            r.aviso(pasta + "/", "apague o LEIA-ME.txt do modelo")
    for dirpath, _, arqs in os.walk(raiz):
        for a in arqs:
            cam = os.path.join(dirpath, a)
            if os.path.getsize(cam) > 20 * 2 ** 20:
                r.aviso(os.path.relpath(cam, raiz), "arquivo com mais de 20 MiB: não entreguem arquivos de teste")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(2)
    raiz = os.path.abspath(args[0])
    r = Relatorio()
    g = carregar_grupo(raiz, r)
    if g:
        for nome, spec in CSVS.items():
            checar_csv(raiz, nome, spec, g, r)
        checar_relatorio(raiz, g, r)
        checar_pastas(raiz, g, r)
    if "--json" in sys.argv:
        print(json.dumps([{"nivel": n, "onde": o, "mensagem": m} for n, o, m in r.itens], ensure_ascii=False, indent=2))
    else:
        for nivel, onde, msg in r.itens:
            print("[%-5s] %-28s %s" % (nivel, onde, msg))
        ne = sum(1 for i in r.itens if i[0] == "ERRO")
        na = sum(1 for i in r.itens if i[0] == "AVISO")
        print()
        print("Resultado: %d erro(s), %d aviso(s). %s" % (ne, na, "Entrega pronta." if ne == 0 else "Corrijam os erros antes de enviar."))
    sys.exit(1 if any(i[0] == "ERRO" for i in r.itens) else 0)


if __name__ == "__main__":
    main()
