# Trabalho prático 2026/II — SimES: simulador de E/S e de sistema de arquivos

Sistemas Operacionais · PUCRS · Prof. Filipo Novo Mór · [filipomor.com](https://filipomor.com)

O enunciado completo (escopo, regras, entrega e avaliação) é distribuído pelo professor.
Este README explica como usar o código.

**Entrega: 26/11/2026, até 23h59.** Cada integrante envia o relatório final no Moodle; o código
fica no repositório público do grupo, citado no relatório.

## Requisitos

- Python 3.8 ou superior, só a biblioteca padrão. Nada exige administrador.
- Opcional: `matplotlib`, para gerar os gráficos (`pip install --user matplotlib`).
- No Windows, troquem `python3` por `py` em todos os comandos.

## Primeiros passos

1. No GitHub (ou outro serviço), criem um repositório **público** novo, vazio, só para este trabalho.
2. Clonem esse repositório e copiem para dentro dele o conteúdo desta pasta:

```bash
cd Aulas_SisOp && git pull && cd ..                     # atualiza o repositório da disciplina
git clone https://github.com/<usuario>/<repositorio>.git
cp -r Aulas_SisOp/Trabalho_IO_2026II/. <repositorio>/   # o "/." copia também o .gitignore
cd <repositorio>
git add . && git commit -m "Esqueleto do SimES" && git push
python3 executar.py testes                              # os testes do núcleo falham até vocês implementarem
```

## Estrutura

| Caminho | Conteúdo | Vocês alteram? |
|---|---|---|
| `simes/parametros.py` | Parâmetros fixos do modelo (disco, CPU, cache) | Não |
| `simes/disco.py` | Modelo do disco rígido; `DiscoFlash` (bônus) | Só o bônus |
| `simes/es/escalonadores.py` | FCFS pronto; SSTF e SCAN (núcleo); C-SCAN, LOOK, C-LOOK, DEADLINE (M2) | Sim |
| `simes/es/cpu.py` | Custo de CPU: polling e interrupção (núcleo); DMA (M3) | Sim |
| `simes/es/cache.py` | Cache LRU e FIFO (M1) | Sim |
| `simes/es/buffering.py` | Buffer simples, duplo e circular (M3) | Sim |
| `simes/es/simulador.py` | Simulador de E/S por eventos | Não |
| `simes/arquivos/sistema.py` | Sistema de arquivos: núcleo, links (M4), proteção e travas (M5) | Sim |
| `simes/arquivos/alocacao.py` | Contígua pronta; encadeada, FAT e indexada (M6) | Sim |
| `simes/arquivos/estruturas.py`, `camada_bloco.py`, `simulador.py` | FCB, tabelas, acesso a blocos, simulador | Não |
| `simes/integracao.py` | Integração ponta a ponta (grupos de 4) | Sim |
| `cargas/` | Cargas padronizadas | Não |
| `experimentos.py` | Experimentos X1 a X13 | Não |
| `graficos.py` | Gráficos padrão | Podem acrescentar |
| `testes/` | Testes automáticos | Podem acrescentar |
| `RELATORIO.md`, `grupo.json` | Modelo do relatório final e dados do grupo | Preencham |
| `ferramentas/validar_entrega.py` | Confere a entrega | Não |

Os pontos a implementar estão marcados com `TODO` e lançam `NotImplementedError` até serem
implementados. As regras de cada um (inclusive as regras de custo do sistema de arquivos)
estão nos comentários do próprio arquivo.

## Comandos

```bash
python3 executar.py testes
python3 executar.py es --carga cargas/es_aleatoria.txt --escalonador SSTF
python3 executar.py es --carga cargas/es_reuso.txt --cache LRU --capacidade 512 --escrita write-back --queda 12000
python3 executar.py arquivos --carga cargas/fs_compilador.txt
python3 executar.py arquivos --carga cargas/fs_alocacao.txt --alocador indexada --blocos 20000
python3 executar.py buffering --buffers 2 --producao 2 --consumo 8
python3 executar.py experimentos           # roda X1 a X13 e grava resultados/
python3 graficos.py                        # gera graficos/ a partir de resultados/
python3 ferramentas/validar_entrega.py     # confere a entrega
```

Os experimentos de módulos não implementados aparecem como `nao_implementado` em
`resultados/experimentos.csv`; isso é esperado para os módulos que o grupo não escolheu.

## Experimentos

| Experimento | Parte | O que compara |
|---|---|---|
| X1 | núcleo | FCFS, SSTF e SCAN em cargas sequencial, aleatória, concentrada e em rajadas |
| X2 | núcleo | Polling × interrupção num disco rígido e num dispositivo rápido |
| X3 | núcleo | Acesso sequencial (compilador) × direto (banco de dados) |
| X4 | núcleo | Custo do `open` conforme a profundidade do caminho |
| X5 | núcleo | Tabelas de arquivos abertos com vários processos |
| X6 | M1 | Cache LRU × FIFO, capacidade, write-through × write-back, queda de energia |
| X7 | M2 | Escalonadores avançados sob carga crescente: inanição e justiça |
| X8 | M3 | Interrupção × DMA conforme o tamanho da requisição; buffering |
| X9 | M4 | Hard links, links simbólicos, ponteiros pendentes e ciclos |
| X10 | M5 | rwx × ACL; travas consultivas × mandatórias |
| X11 | M6 | Alocação contígua × encadeada × FAT × indexada |
| X12 | integração | Cargas de arquivos passando pela cache e pelo escalonador |
| X13 | bônus | Armazenamento flash × disco rígido |

## Entrega (até 26/11/2026, 23h59)

1. Rodem `python3 executar.py experimentos` e `python3 graficos.py`, e façam commit também de
   `resultados/` e `graficos/`: o relatório cita esses arquivos como evidência.
2. Preencham `grupo.json` (nomes completos, link do repositório, módulos escolhidos) e
   `RELATORIO.md` (no topo: o nome completo de TODOS os integrantes e o link do repositório).
3. Rodem `python3 ferramentas/validar_entrega.py` até não haver erros, e deem `git push`.
4. Confiram que o repositório é público: abram o link numa janela anônima do navegador.
5. Exportem o relatório para PDF (por exemplo: abram o `RELATORIO.md` no GitHub e usem
   Imprimir → Salvar como PDF).
6. **Cada integrante** envia o PDF do relatório no Moodle. Só o relatório é enviado; código,
   resultados e gráficos ficam no repositório.

O professor considera o repositório no estado em que estava no prazo de entrega; commits
posteriores podem ser desconsiderados.

## Dados sensíveis

O repositório é público. **Não incluam** matrícula, e-mail, telefone, CPF ou outros dados
pessoais; senhas, tokens ou chaves de API; arquivos `.env` ou de configuração pessoal. Os nomes
dos integrantes aparecem no relatório e no `grupo.json`; nada além disso.

O validador procura alguns desses padrões, mas a responsabilidade é do grupo. Se algo sensível
for parar num commit, apagar o arquivo depois não basta: ele continua no histórico do git.
Troquem a senha ou o token imediatamente e, se for o caso, recriem o repositório.
