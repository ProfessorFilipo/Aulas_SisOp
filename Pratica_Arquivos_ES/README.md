# Atividade prática — Arquivos e E/S na prática

Sistemas Operacionais · PUCRS · Prof. Filipo Novo Mór · [filipomor.com](https://filipomor.com)

Seis estações curtas, em duplas, no ciclo **prever → executar → explicar**.
Cada script para antes de cada experimento e pede a previsão da dupla.
Tudo o que for previsto e observado fica em `_lab/registro_da_dupla.md`.

Só usa a biblioteca padrão do Python 3.8+. Funciona em **Linux, macOS e Windows**.

| Sistema | Como rodar |
|---|---|
| Linux / macOS | `python3 e1_identidade_links.py` |
| Windows | `py e1_identidade_links.py` (ou `python`) |

## Preparação

```bash
git clone https://github.com/ProfessorFilipo/Aulas_SisOp.git   # ou: git pull
cd Aulas_SisOp/Pratica_Arquivos_ES
python3 00_verificar_ambiente.py
```

## Estações

| Arquivo | Tema | Silberschatz (9ª ed.) |
|---|---|---|
| `e1_identidade_links.py` | Identidade do arquivo, hard link e link simbólico | 11.1.1, 11.3.4 |
| `e2_arquivo_aberto.py` | Tabelas de arquivos abertos, `dup()`, apagar arquivo em uso | 11.1.2 |
| `e3_buffers.py` | Buffer do processo × cache do kernel × disco, `flush` × `fsync` | 13.4.2, 13.4.3, 11.5.3 |
| `e4_volumes.py` | Volumes, tipos de sistema de arquivos, EXDEV, montagem | 11.3.1, 11.4 |
| `e5_protecao.py` | Bits rwx × ACL, permissão do diretório | 11.6 |
| `e6_interrupcoes.py` | Interrupções e DMA medidos em quatro fases | 13.2.2, 13.2.3, 13.5 |
| `extra_bloqueio.py` | Desafio: bloqueio consultivo × mandatório | 11.1.2 |
| `99_limpar.py` | Apaga `_lab/` (copia antes o registro para esta pasta) | — |

## Sem administrador

Nenhuma estação exige `sudo` ou Administrador; rodem tudo como usuário comum.

* `--sem-pausa`: roda sem pedir previsões (demonstração no projetor).
* Estação 4, Linux: a montagem é feita em um *namespace* próprio (`unshare`). Se o sistema
  recusar (o Ubuntu 24.04 pode recusar via AppArmor), o script explica o motivo.
* Estação 4, macOS: sem um segundo volume gravável, o script cria um com uma imagem de disco
  (`hdiutil`), que o `99_limpar.py` desmonta.
* Estação 5, Linux: sem o `setfacl`, a ACL é gravada direto pela chamada de sistema.
* Estação 6, macOS: sem administrador, o disco é observado pelo `iostat`. Contas de
  administrador podem rodar `sudo python3 e6_interrupcoes.py` para ver as interrupções.

## Observações por sistema

* **Windows:** links simbólicos exigem Administrador ou o *Modo de Desenvolvedor*. Sem isso,
  a estação 1 mostra o erro e demonstra uma junção de diretório (`mklink /J`) no lugar.
  O segundo volume da estação 4 depende de um pendrive.
* Nenhum script grava fora de `_lab/`, exceto a busca por um segundo volume na estação 4,
  que cria e apaga uma pasta temporária `sisop_e4_*`.
