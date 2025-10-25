/********************************************************************************
***      C O M P A R A C A O    A L G O R I T M O S   F I F O   vs   L R U    ***
*********************************************************************************
*** Prof. Filipo Mor - github.com/ProfessorFilipo                             ***
********************************************************************************/

#include <stdio.h>

#define MAX 10

/* Função FIFO */
int fifo(int refs[], int n, int capacity) 
{
    int frames[MAX], next = 0, faults = 0;
    for (int i = 0; i < capacity; i++) frames[i] = -1;

    for (int i = 0; i < n; i++) 
    {
        int ref = refs[i], hit = 0;
        for (int j = 0; j < capacity; j++) if (frames[j] == ref) hit = 1;
        if (!hit) 
        {                        /* page fault */
            frames[next] = ref;
            next = (next + 1) % capacity;  /* substitui circularmente */
            faults++;
        }
    }
    return faults;
}

/* Função LRU (Least Recently Used) */
int lru(int refs[], int n, int capacity) 
{
    int frames[MAX], lastUsed[MAX], faults = 0;
    for (int i = 0; i < capacity; i++) frames[i] = -1;

    for (int i = 0; i < n; i++) 
    {
        int ref = refs[i], hit = 0;
        for (int j = 0; j < capacity; j++) 
        {  /* verifica se já está na memória */
            if (frames[j] == ref) 
            {
                hit = 1;
                lastUsed[j] = i;             /* atualiza tempo de uso */
                break;
            }
        }
        if (!hit) 
        {                          /* page fault */
            int pos = -1;
            if (i < capacity) pos = i;       /* ainda há espaço */
            else 
            {
                /* encontra a menos recentemente usada */
                int min = 9999;
                for (int j = 0; j < capacity; j++)
                    if (lastUsed[j] < min) { min = lastUsed[j]; pos = j; }
            }
            frames[pos] = ref;
            lastUsed[pos] = i;
            faults++;
        }
    }
    return faults;
}

int main(void) 
{
    int refs[] = {1, 2, 3, 1, 4, 2, 5}; // sequencia de acesso as páginas de memória
    int n = sizeof(refs)/sizeof(refs[0]);
    int capacity = 3;

    int f_fifo = fifo(refs, n, capacity);
    int f_lru  = lru(refs, n, capacity);

    printf("Comparação FIFO x LRU (frames = %d)\n", capacity);
    printf("Sequência: ");
    for (int i = 0; i < n; i++) printf("%d ", refs[i]);
    printf("\n\nPage Faults:\n");
    printf("FIFO = %d\n", f_fifo);
    printf("LRU  = %d\n", f_lru);
    return 0;
}
