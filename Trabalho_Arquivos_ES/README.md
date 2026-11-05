# Trabalho prático — Mesma chamada, comportamentos diferentes

Sistemas Operacionais · PUCRS · Prof. Filipo Novo Mór · [filipomor.com](https://filipomor.com)

O enunciado completo está no documento distribuído pelo professor. Esta pasta contém:

| Caminho | Para quê |
|---|---|
| `template_entrega/` | Modelo da entrega. Copiem a pasta, renomeiem e preencham. |
| `ferramentas/coletar_ambiente.py` | Registra o ambiente de testes (SO, CPU, RAM, sistemas de arquivos) em JSON. |
| `ferramentas/validar_entrega.py` | Confere estrutura, CSVs, relatório e evidências antes do envio. |

```bash
cp -r template_entrega ~/tp_sisop_entrega
python3 ferramentas/coletar_ambiente.py --sistema S1 --saida ~/tp_sisop_entrega/ambiente --caminhos ~/tp_teste /media/$USER/PENDRIVE/tp_teste
python3 ferramentas/validar_entrega.py ~/tp_sisop_entrega
```

No Windows, troquem `python3` por `py`.

## Dicionário dos arquivos de resultados

Separador: vírgula. Decimal: ponto. Codificação: UTF-8. Uma linha por execução (repetição).
Os valores das colunas marcadas com uma lista **devem** ser exatamente um dos valores listados.
Colunas que não se aplicam ficam vazias.

### `resultados/A_desempenho.csv`

| Coluna | Conteúdo |
|---|---|
| `experimento` | `A1` · `A2` · `A3` · `A4` · `A5` · `A6` |
| `sistema` | ID do sistema em `grupo.json` (`S1`, `S2`...) |
| `sf` | ID do sistema de arquivos em `grupo.json` (`F1`, `F2`...) |
| `operacao` | `leitura` · `escrita` |
| `padrao_acesso` | `sequencial` · `aleatorio` |
| `tamanho_bloco_bytes` | tamanho de cada chamada de leitura/escrita |
| `tamanho_total_bytes` | total transferido na execução |
| `estado_cache` | `frio` · `quente` · `nao_se_aplica` |
| `modo_durabilidade` | `nenhum` · `fsync_final` · `fsync_cada` · `o_sync` · `o_dsync` · `write_through` · `full_fsync` · `nao_se_aplica` |
| `modo_es` | `bufferizada` · `direta` |
| `repeticao` | 1, 2, 3... (mínimo de 5 por configuração) |
| `tempo_s` | tempo de parede, em segundos |
| `vazao_mib_s` | MiB/s |
| `operacoes_por_s` | chamadas por segundo (A2, A4) |
| `cpu_usuario_s`, `cpu_sistema_s` | tempo de CPU do processo, em segundos |
| `interrupcoes_disco` | só A6: interrupções da controladora durante a execução |
| `log` | caminho do log bruto, ex.: `logs/A1_S1_F1.log` |

### `resultados/B_modelos_es.csv`

| Coluna | Conteúdo |
|---|---|
| `experimento` | `B0` · `B1` · `B2` · `B3` · `B4` |
| `sistema` | ID do sistema |
| `modelo` | `sequencial_bloqueante` · `thread_por_cliente` · `nao_bloqueante_polling` · `multiplexado` · `assincrono` |
| `mecanismo` | texto livre curto: `select`, `poll`, `epoll`, `kqueue`, `iocp`, `threads`... |
| `n_clientes_lentos` | número de clientes lentos conectados |
| `repeticao` | 1, 2, 3... (mínimo de 5, exceto quando `falhou=sim`) |
| `duracao_s` | duração da medição |
| `latencia_sonda_media_ms`, `latencia_sonda_p95_ms` | latência do cliente sonda |
| `vazao_total_kib_s` | KiB/s entregues a todos os clientes |
| `cpu_usuario_s`, `cpu_sistema_s` | CPU do processo servidor |
| `threads_max`, `descritores_max` | máximos observados no servidor |
| `falhou` | `sim` · `nao` |
| `motivo_falha` | erro observado, pelo nome: `EMFILE`, `ValueError: filedescriptor out of range in select()`... |
| `log` | caminho do log bruto |

### `resultados/C_conformidade.csv`

| Coluna | Conteúdo |
|---|---|
| `teste` | `C1` ... `C12` |
| `sistema`, `sf` | IDs de `grupo.json` |
| `caso` | identificador curto do caso, ex.: `hardlink_outro_volume`, `nome_CON`, `mtime_ns` |
| `hipotese` | o que o grupo esperava, em uma frase |
| `observado` | o que aconteceu, em uma frase |
| `codigo_erro` | nome do erro, se houve: `EXDEV`, `ELOOP`, `WinError 32`... |
| `confirmou_hipotese` | `sim` · `nao` |
| `log` | caminho do log bruto |
