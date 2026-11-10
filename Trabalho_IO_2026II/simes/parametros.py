# -*- coding: utf-8 -*-
"""
Parâmetros fixos do modelo de simulação.

NÃO ALTEREM ESTES VALORES: todos os grupos usam os mesmos parâmetros, para que
os resultados possam ser comparados. Se quiserem explorar outros valores, façam
isso em um experimento extra, declarado no relatório.

Unidade de tempo: milissegundos (ms).
"""

# --------------------------------------------------------------- armazenamento
TAMANHO_BLOCO = 4096                      # bytes por bloco
CILINDROS = 5000                          # cilindros do disco: 0 .. 4999
BLOCOS_POR_CILINDRO = 64
TOTAL_BLOCOS = CILINDROS * BLOCOS_POR_CILINDRO   # 320.000 blocos (cerca de 1,2 GiB)

# ------------------------------------------------------- disco rígido (HDD)
# Tempo de atendimento de uma requisição de n blocos que começa no bloco b:
#   busca      = 0, se o braço já está no cilindro de b;
#              = BUSCA_MINIMA_MS + distância_em_cilindros * BUSCA_POR_CILINDRO_MS, caso contrário
#   rotação    = 0, se b é exatamente o bloco seguinte ao último bloco transferido
#                   (leitura/escrita em sequência, sem perder a volta);
#              = LATENCIA_ROTACIONAL_MS, caso contrário (meia volta, em média)
#   transferência = n * TRANSFERENCIA_MS_POR_BLOCO
BUSCA_MINIMA_MS = 1.0
BUSCA_POR_CILINDRO_MS = 0.003
LATENCIA_ROTACIONAL_MS = 4.17             # meia volta a 7.200 rpm
TRANSFERENCIA_MS_POR_BLOCO = 0.04         # cerca de 100 MB/s

# Dispositivo rápido (sem partes móveis), usado no experimento X2.
DISPOSITIVO_RAPIDO = dict(
    busca_minima_ms=0.0,
    busca_por_cilindro_ms=0.0,
    latencia_rotacional_ms=0.0,
    transferencia_ms_por_bloco=0.008,
)

# ------------------------------------------------------------------------ CPU
CUSTO_INTERRUPCAO_MS = 0.015              # tratar uma interrupção, incluindo a troca de contexto
CUSTO_COPIA_MS_POR_BLOCO = 0.002          # CPU copiando um bloco entre a controladora e a memória
CUSTO_PROGRAMAR_DMA_MS = 0.003            # CPU programando a controladora de DMA

# ------------------------------------------------------- cache de blocos (M1)
CUSTO_ACERTO_CACHE_MS = 0.001             # atender um bloco a partir da memória
INTERVALO_SYNC_MS = 5000.0                # gravação periódica dos blocos sujos (write-back)

# --------------------------------------------------------------- deadline (M2)
# O mq-deadline do Linux usa 500 ms e 5 s em discos reais; aqui os prazos foram
# reduzidos para a escala de tempo do disco simulado.
PRAZO_LEITURA_MS = 200.0
PRAZO_ESCRITA_MS = 2000.0

# ------------------------------------------------------------- flash (bônus)
FLASH_PAGINAS_POR_BLOCO_APAGAVEL = 64     # uma página = um bloco de 4 KiB
FLASH_LEITURA_MS = 0.025                  # ler uma página
FLASH_PROGRAMACAO_MS = 0.2                # gravar uma página (só em página apagada)
FLASH_APAGAMENTO_MS = 1.5                 # apagar um bloco apagável inteiro
FLASH_AREA_RESERVA = 0.07                 # 7% de páginas extras, invisíveis ao sistema
