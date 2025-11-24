#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MEM_SIZE 3     // capacidade da memória principal
#define DISK_SIZE 20   // capacidade da memória secundária

typedef struct {
    int id;
    int active;  // 1 = presente, 0 = vazio
} Process;

// Memória principal e secundária
Process memory[MEM_SIZE];
Process disk[DISK_SIZE];

// Quantidade de processos na memória e no disco
int memCount = 0;
int diskCount = 0;

// Inicializa ambas as memórias
void init() {
    for (int i = 0; i < MEM_SIZE; i++) {
        memory[i].active = 0;
    }
    for (int i = 0; i < DISK_SIZE; i++) {
        disk[i].active = 0;
    }
}

// Imprime estado atual
void printState() {
    printf("\n=== Estado Atual ===\n");
    
    printf("Memória Principal:\n");
    for (int i = 0; i < MEM_SIZE; i++) {
        if (memory[i].active)
            printf("  Slot %d -> Processo %d\n", i, memory[i].id);
        else
            printf("  Slot %d -> [vazio]\n", i);
    }

    printf("\nMemória Secundária (Disco):\n");
    for (int i = 0; i < diskCount; i++) {
        printf("  Processo %d\n", disk[i].id);
    }
    if (diskCount == 0) printf("  [vazio]\n");

    printf("====================\n\n");
}

// Realiza swap-out do processo mais antigo (posição 0 da memória)
void swapOut() {
    if (memCount == 0) return;

    printf("Swap-out: Processo %d movido para o disco.\n", memory[0].id);

    // Move para a memória secundária
    disk[diskCount++] = memory[0];

    // Faz shift para remover o primeiro processo da memória
    for (int i = 0; i < MEM_SIZE - 1; i++) {
        memory[i] = memory[i + 1];
    }
    memory[MEM_SIZE - 1].active = 0;

    memCount--;
}

// Adiciona processo na memória (faz swap-out se necessário)
void addProcess(int id) {
    printf("\nSolicitação: adicionar processo %d.\n", id);

    // Se memória está cheia, realizar swap-out
    if (memCount == MEM_SIZE) {
        swapOut();
    }

    // Adiciona no primeiro slot vazio
    for (int i = 0; i < MEM_SIZE; i++) {
        if (!memory[i].active) {
            memory[i].id = id;
            memory[i].active = 1;
            memCount++;
            printf("Processo %d carregado na memória.\n", id);
            break;
        }
    }
}

int main() {
    init();

    int opcao, pid;

    while (1) {
        printf("\n=== Simulador de Swapping ===\n");
        printf("1 - Adicionar processo\n");
        printf("2 - Mostrar estado\n");
        printf("3 - Sair\n");
        printf("Escolha: ");
        scanf("%d", &opcao);

        switch (opcao) {
            case 1:
                printf("ID do processo: ");
                scanf("%d", &pid);
                addProcess(pid);
                break;
            case 2:
                printState();
                break;
            case 3:
                printf("Encerrando.\n");
                return 0;
            default:
                printf("Opcao invalida.\n");
        }
    }

    return 0;
}
