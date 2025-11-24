#include <stdio.h>
#include <stdlib.h>

#define MEM_SIZE 3     // capacidade da memória principal
#define DISK_SIZE 20   // capacidade da memória secundária

typedef struct {
    int id;
    int active;     // 1 = ocupado, 0 = vazio
    int lastUsed;   // tempo lógico do último uso
} Process;

// Memória principal e secundária
Process memory[MEM_SIZE];
Process disk[DISK_SIZE];

int memCount = 0;
int diskCount = 0;

int globalTime = 0;   // contador de tempo lógico para LRU

void init() {
    for (int i = 0; i < MEM_SIZE; i++) {
        memory[i].active = 0;
        memory[i].lastUsed = 0;
    }
    for (int i = 0; i < DISK_SIZE; i++) {
        disk[i].active = 0;
        disk[i].lastUsed = 0;
    }
}

// Função auxiliar: imprime estado atual
void printState() {
    printf("\n=== Estado Atual ===\n");

    printf("Memória Principal:\n");
    for (int i = 0; i < MEM_SIZE; i++) {
        if (memory[i].active)
            printf("  Slot %d -> Processo %d (lastUsed=%d)\n", 
                    i, memory[i].id, memory[i].lastUsed);
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

// Seleciona o processo LRU para swap-out
int findLRU() {
    int lruIndex = -1;
    int minTime = 999999999;

    for (int i = 0; i < MEM_SIZE; i++) {
        if (memory[i].active && memory[i].lastUsed < minTime) {
            minTime = memory[i].lastUsed;
            lruIndex = i;
        }
    }

    return lruIndex;
}

// Realiza swap-out baseado em LRU
void swapOut() {
    int index = findLRU();
    if (index < 0) return;

    printf("Swap-out (LRU): Processo %d removido.\n", memory[index].id);

    // Move para o disco
    disk[diskCount++] = memory[index];

    // Remove da memória
    memory[index].active = 0;
    memCount--;
}

// Acessa (ou insere) um processo → atualiza tempo lógico
void touchProcess(int index) {
    globalTime++;
    memory[index].lastUsed = globalTime;
}

// Adiciona um novo processo
void addProcess(int id) {
    printf("\nSolicitação: adicionar processo %d.\n", id);

    // Se memória cheia → swap-out pelo LRU
    if (memCount == MEM_SIZE) {
        swapOut();
    }

    // Inserir no primeiro slot vazio
    for (int i = 0; i < MEM_SIZE; i++) {
        if (!memory[i].active) {
            memory[i].id = id;
            memory[i].active = 1;
            touchProcess(i);
            memCount++;
            printf("Processo %d carregado na memória.\n", id);
            return;
        }
    }
}

// Simular acesso a processo já carregado → atualiza lastUsed
void accessProcess(int id) {
    for (int i = 0; i < MEM_SIZE; i++) {
        if (memory[i].active && memory[i].id == id) {
            printf("Acesso ao processo %d.\n", id);
            touchProcess(i);
            return;
        }
    }
    printf("Processo %d não está na memória.\n", id);
}

int main() {
    init();

    int opcao, pid;

    while (1) {
        printf("\n=== Simulador de Swapping (LRU) ===\n");
        printf("1 - Adicionar processo\n");
        printf("2 - Acessar processo\n");
        printf("3 - Mostrar estado\n");
        printf("4 - Sair\n");
        printf("Escolha: ");
        scanf("%d", &opcao);

        switch (opcao) {
            case 1:
                printf("ID do processo: ");
                scanf("%d", &pid);
                addProcess(pid);
                break;
            case 2:
                printf("ID do processo: ");
                scanf("%d", &pid);
                accessProcess(pid);
                break;
            case 3:
                printState();
                break;
            case 4:
                printf("Encerrando.\n");
                return 0;
            default:
                printf("Opcao invalida.\n");
        }
    }

    return 0;
}
