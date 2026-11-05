# Relatório — Mesma chamada, comportamentos diferentes

<!--
INSTRUÇÕES DO MODELO (apague este bloco antes de entregar)
- Mantenha EXATAMENTE os títulos numerados (## 0. ... ## 8.) e os campos em negrito.
- Cada experimento realizado tem uma seção "### <ID> — <título>" (IDs: A1–A6, B, C1–C12).
  Apague as seções dos experimentos que o grupo NÃO fez (de acordo com grupo.json).
- Substitua todo texto entre colchetes [ ... ] pelo conteúdo do grupo.
- O campo **Veredito:** aceita só: CONFIRMADA, PARCIALMENTE CONFIRMADA ou REFUTADA.
- Em **Evidências:**, cite caminhos que existam na entrega (logs/..., resultados/..., graficos/...).
- Rode  python3 ferramentas/validar_entrega.py <pasta_da_entrega>  antes de enviar.
-->

## 0. Resumo

[Até 10 linhas: o que o grupo investigou, em quais sistemas, e os 3 achados mais importantes.]

## 1. Ambiente de testes

| ID | Sistema operacional (versão) | Máquina (CPU, RAM) | Virtualizado? |
|----|------------------------------|--------------------|---------------|
| S1 | [ex.: Ubuntu 24.04, kernel 6.8] | [ex.: Intel i5-1235U, 16 GB] | [não] |

| ID | Sistema | Tipo de SF | Dispositivo | Caminho de teste |
|----|---------|-----------|-------------|------------------|
| F1 | S1 | [ext4] | [SSD NVMe interno] | [/home/aluno/tp_sisop] |

Arquivos de coleta: [ambiente/ambiente_S1.json]

## 2. Metodologia comum

- **Medição de tempo:** [relógio usado, ex.: time.perf_counter / clock_gettime(CLOCK_MONOTONIC)]
- **Medição de CPU:** [ex.: resource.getrusage / os.times / GetProcessTimes]
- **Repetições:** [número por configuração; se a 1ª foi descartada como aquecimento, diga]
- **Como esvaziamos o cache em cada sistema:** [comandos ou técnica, por sistema]
- **Controle de ruído:** [ex.: na tomada, modo de energia, programas fechados, ordem das execuções intercalada]
- **Como reproduzir tudo:** `[ex.: cd codigo && ./executar_tudo.sh /caminho/de/teste]`

## 3. Experimentos

### A1 — Tamanho de bloco

**Hipótese:** [escrita ANTES de executar]

**Fundamentação:** [por que vocês esperavam isso; cite seções do Silberschatz]

**Procedimento:** [comando exato e parâmetros; tamanhos de bloco; tamanho do arquivo]

**Resultados:** [tabela com média ± desvio padrão por configuração; gráfico em graficos/A1.png]

**Evidências:** [logs/A1_S1_F1.log; resultados/A_desempenho.csv (experimento=A1); graficos/A1.png]

**Análise:** [explicação dos resultados, inclusive o que contrariou a hipótese]

**Veredito:** [CONFIRMADA | PARCIALMENTE CONFIRMADA | REFUTADA]

### A2 — Acesso sequencial × aleatório

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Procedimento:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### A3 — Cache frio × quente

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Procedimento:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### A4 — Custo da durabilidade

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Procedimento:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### A5 — E/S direta × bufferizada

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Procedimento:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### A6 — Interrupções e DMA sob carga

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Procedimento:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### B — Modelos de E/S com muitas conexões

**Hipótese:** [uma por modelo B0–B4: latência da sonda, CPU e limite de clientes esperados]

**Fundamentação:** [ ]

**Procedimento:** [parâmetros do cliente lento e da sonda; valores de N; mecanismo nativo usado em cada SO]

**Resultados:** [tabela modelo × N com latência média, p95 e CPU; gráficos em graficos/B_*.png]

**Evidências:** [ ]

**Análise:** [qual modelo atende o requisito 2 do Dossiê 01 e por quê; o que limitou cada modelo]

**Veredito:** [ ]

### C1 — Hard links

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Procedimento:** [ ]

**Resultados:** [resultado em cada sistema de arquivos testado]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### C2 — Links simbólicos e ciclos

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Procedimento:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### C3 — Apagar e renomear arquivo aberto

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Procedimento:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### C4 — Bloqueio consultivo × mandatório

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Procedimento:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### C5 — Maiúsculas e minúsculas

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Procedimento:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### C6 — Nomes proibidos e reservados

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Procedimento:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### C7 — Limites de nome e de caminho

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Procedimento:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### C8 — Resolução das datas

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Procedimento:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### C9 — Permissões em cada sistema de arquivos

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Procedimento:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### C10 — Arquivos esparsos e tamanho máximo

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Procedimento:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### C11 — Substituição atômica com leitor ativo

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Procedimento:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### C12 — Acréscimos concorrentes

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Procedimento:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### Matriz de conformidade (Parte C)

| Teste | [S1/F1] | [S1/F2] | [S2/F3] |
|-------|---------|---------|---------|
| C1 | [ ] | [ ] | [ ] |

## 4. Análise cruzada entre sistemas

[Obrigatória para grupos de 4 integrantes. Para cada diferença relevante entre sistemas
operacionais ou sistemas de arquivos: o que mudou, a decisão de projeto que explica a
diferença e a consequência prática para quem desenvolve software.]

## 5. Ameaças à validade

[O que pode ter distorcido os resultados: cache, bateria, outros programas, máquina virtual,
tamanho dos arquivos, precisão do relógio, número de repetições...]

## 6. Conclusões

[O que o grupo aprendeu; 3 a 6 itens objetivos.]

## 7. Referências

- SILBERSCHATZ, A.; GALVIN, P. B.; GAGNE, G. *Operating System Concepts*. 9. ed. Wiley, 2013.
- [Páginas de manual, documentação oficial e artigos consultados, com link]

## 8. Declaração de autoria e uso de ferramentas

[Quem fez o quê. Código ou texto de terceiros, inclusive de ferramentas de IA, com a indicação
de onde foi usado.]
