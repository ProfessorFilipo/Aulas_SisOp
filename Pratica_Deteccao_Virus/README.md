# Atividade prática — O antivírus por dentro

Sistemas Operacionais · PUCRS · Prof. Filipo Novo Mór · [filipomor.com](https://filipomor.com)

Atividade em **duplas**, feita **em aula** (cerca de 1h15). **Não há entrega.** O
roteiro completo está no arquivo `Roteiro_Deteccao_Virus.docx`, nesta mesma pasta.

Esta é uma aula de **gestão de arquivos**: vocês vão fazer o sistema de arquivos
dizer, em Python puro, **o que** cada arquivo é (tipo, pelo conteúdo e não pela
extensão), **onde** o nome e o conteúdo moram, e **o que mudou** (integridade e
atributos do FCB/inode). O antivírus é só a lente que dá sentido a tudo isso.

## Requisitos

- Python 3.8 ou superior, **só a biblioteca padrão**. Não instala nada.
- **Nada exige administrador.** O programa apenas **lê** arquivos de uma pasta de amostras.
- Funciona igual em **Windows, macOS e Linux**. No Windows, troquem `python3` por `py`.

## Como obter e rodar

```bash
cd Aulas_SisOp && git pull        # atualiza o repositório da disciplina
cd Pratica_Deteccao_Virus
python3 detector.py               # no Windows: py detector.py
```

O programa já roda desde o início. Cada etapa que ainda não foi implementada aparece
como `(TODO)` no relatório, então dá para implementar e rodar **uma etapa de cada vez**.

## O que implementar

Abram `detector.py` e preencham os seis trechos marcados com `TODO`:

| Etapa | Função | O que faz |
|---|---|---|
| 1 | `identificar_tipo` | Tipo real pelo *magic number* (os primeiros bytes do conteúdo) |
| 2 | `varrer_pragas` | Procura assinaturas de praga em qualquer posição do arquivo |
| 3 | `extensao_coerente` | Acusa quando o nome (extensão) não bate com o conteúdo |
| 4A | `sha256_arquivo` | Calcula o hash SHA-256 do conteúdo |
| 4B | `verificar_integridade` | Percorre uma pasta e acha o que mudou em relação à linha de base |
| 4C | `atributos` | Lê o tamanho e a data que o FCB/inode guarda (`os.stat`) |

A etapa 4C alimenta uma demonstração pronta: a **data de um arquivo é forjável**
(`os.utime`), mas o **hash do conteúdo** não — metadado × conteúdo.

As instruções de cada função estão no próprio `detector.py`, logo acima do `TODO`.

## Estrutura da pasta

| Caminho | Conteúdo |
|---|---|
| `detector.py` | O programa que vocês completam |
| `base_assinaturas.json` | Tipos conhecidos (magic numbers) e assinaturas de praga |
| `amostras/` | Arquivos para as etapas 1 a 3 (todos inofensivos) |
| `instalacao/` | Uma "instalação" íntegra, de referência |
| `instalacao_depois/` | A mesma instalação, com um arquivo adulterado (etapa 4) |
| `linha_de_base.json` | Os hashes da instalação íntegra |
| `Roteiro_Deteccao_Virus.docx` | O roteiro completo da atividade |

## Observações

- As "pragas" desta atividade são **assinaturas inventadas**, só para a aula. Nenhum
  arquivo aqui é um programa de verdade nem contém código malicioso: são apenas bytes
  de cabeçalho seguidos de texto.
- Este repositório é **público**. A atividade não pede nenhum dado pessoal de vocês;
  não incluam matrícula, e-mail ou outro dado pessoal em arquivos que forem versionar.
