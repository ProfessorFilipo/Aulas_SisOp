# Gestão de Entrada e Saída

Exemplos práticos da aula de **Gestão de Entrada e Saída** da disciplina de Sistemas Operacionais (PUCRS).
Base teórica: Silberschatz, Galvin & Gagne, *Operating System Concepts*, 9ª ed., capítulo 13 (I/O Systems).

Os exemplos funcionam em **Ubuntu/Debian** e em **macOS** (Apple Silicon ou Intel).
Usam só a biblioteca padrão do Python (3.8 ou mais recente) e um compilador C.

## Antes da aula

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y git python3 build-essential
git clone https://github.com/ProfessorFilipo/Aulas_SisOp.git
cd Aulas_SisOp/Gestao_IO
sh 00_verificar_ambiente.sh
```

### macOS

```bash
xcode-select --install        # instala python3, cc e git (Command Line Tools)
git clone https://github.com/ProfessorFilipo/Aulas_SisOp.git
cd Aulas_SisOp/Gestao_IO
sh 00_verificar_ambiente.sh
```

O verificador deve terminar com **"Tudo pronto para a aula!"**.
Se você já tinha clonado o repositório, basta atualizar com `git pull` dentro da pasta `Aulas_SisOp`.

## Exemplos da aula

Rode sempre de dentro da pasta `Gestao_IO`, direto no terminal.

| # | Tópico | Seção do livro | Comando |
|---|--------|----------------|---------|
| 0 | Verificação do ambiente | — | `sh 00_verificar_ambiente.sh` |
| 1 | Hardware: barramentos, controladoras, portas, E/S mapeada em memória | 13.2 | `python3 01_hardware.py` |
| 2 | Polling × interrupções | 13.2.1–13.2.3 | `python3 02_polling_vs_interrupcao.py` |
| 3 | Dispositivos de bloco e de caractere, `ioctl()` | 13.3, 13.3.1 | `python3 03_dispositivos_ioctl.py` |
| 4 | E/S bloqueante, não bloqueante e `select()` com sockets | 13.3.2–13.3.5 | `python3 04_bloqueio_select.py` |
| 5 | Escalonamento de E/S, cache e escrita adiada | 13.4.1–13.4.4 | `python3 05_escalonamento_cache.py` |
| 6 | Erros (`errno`) e proteção de E/S | 13.4.5–13.4.8 | `python3 06_erros_protecao.py` |
| 7 | Do nome do arquivo até a controladora | 13.5 | `python3 07_traducao_nomes.py` |
| 8 | STREAMS e disciplina de linha do terminal | 13.6 | `python3 08_disciplina_linha.py` |
| 9 | Desempenho: o custo das chamadas de sistema | 13.7 | `python3 09_desempenho.py` |
| + | Para casa: relógios, `mmap` e E/S vetorizada | 13.3.1, 13.3.3, 13.3.5 | `python3 extra_relogios_mmap_writev.py` |

Os demais arquivos são de apoio: `comum.py` (funções compartilhadas) e `privilegiada.c` (usado pelo exemplo 6).

## Observações

- **Nenhum exemplo precisa de `sudo` no Linux.** Opcional: `sudo python3 01_hardware.py` mostra os endereços reais das portas de E/S.
- **No macOS, o exemplo 5 pede a senha de administrador** para rodar `sudo purge`, que esvazia o cache de disco.
- O exemplo 5 cria o arquivo `dados_teste.bin` (128 MB). Ao final, apague com `rm dados_teste.bin`.
- Os exemplos 3 e 8 são interativos: no 3, redimensione a janela do terminal; no 8, digite teclas e termine com `q`.
- Em máquinas virtuais ou no WSL, os dispositivos mostrados são virtuais (por exemplo, `vda` ou `virtio`).

## Linux × macOS: o que muda

| Assunto | Linux (x86) | macOS (Apple Silicon) |
|---------|-------------|-----------------------|
| E/S por portas (instruções IN/OUT) | existe (`/proc/ioports`) | não existe: só E/S mapeada em memória |
| Valor de `EAGAIN` | 11 | 35 |
| `<major, minor>` de `/dev/null` | `<1, 3>` | `<3, 2>` |
| Garantir que o dado chegou ao disco | `fsync()` | `fcntl(F_FULLFSYNC)` |
| Instrução privilegiada em modo usuário | sinal `SIGSEGV` | sinal `SIGILL` |

---
Prof. Filipo Novo Mór · [filipomor.com](https://filipomor.com) · [github.com/ProfessorFilipo](https://github.com/ProfessorFilipo)
