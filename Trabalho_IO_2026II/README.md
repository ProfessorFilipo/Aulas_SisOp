# Trabalho prático 2026/II — SimES: simulador de E/S e de sistema de arquivos

Sistemas Operacionais · PUCRS · Prof. Filipo Novo Mór · [filipomor.com](https://filipomor.com)

O enunciado completo (escopo, regras, entrega e avaliação) é distribuído pelo professor.
Este README explica como usar o código.

**Entrega: 24/11/2026, até 23h59.**

## Requisitos

- Python 3.8 ou superior, só a biblioteca padrão. Nada exige administrador.
- Opcional: `matplotlib`, para gerar os gráficos (`pip install --user matplotlib`).
- No Windows, troquem `python3` por `py` em todos os comandos.

## Primeiros passos

```bash
git pull                                   # no repositório Aulas_SisOp
cp -r Trabalho_IO_2026II ~/meu_trabalho    # trabalhem numa CÓPIA da pasta
cd ~/meu_trabalho
python3 executar.py testes                 # os testes do núcleo falham até vocês implementarem
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
| `RELATORIO.md`, `grupo.json` | Modelos da entrega | Preencham |
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

## Entrega

1. `python3 executar.py experimentos` e `python3 graficos.py`.
2. Preencham `grupo.json` e `RELATORIO.md`.
3. `python3 ferramentas/validar_entrega.py` até não haver erros.
4. Apaguem as pastas `__pycache__` e compactem a pasta inteira em `SisOp_TP_IO_<sobrenomes>.zip`.
5. Um integrante envia o arquivo pelo Moodle até **24/11/2026, 23h59**.
