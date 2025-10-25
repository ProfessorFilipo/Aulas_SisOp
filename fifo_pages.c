/********************************************************************************
***            D E M O N S T R A C A O    A L G O R I T M O   F I F O         ***
*********************************************************************************
*** Prof. Filipo Mor - github.com/ProfessorFilipo                             ***
********************************************************************************/
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int page_refs[] = {1, 2, 3, 4, 1, 5};   /* sequência de referência */
    int n = sizeof(page_refs) / sizeof(page_refs[0]);
    int capacity = 3;                       /* número de frames */
    int frames[10];                         /* alocar um pouco a mais */
    int i, j;

    /* inicializar frames com -1 (vazio) */
    for (i = 0; i < capacity; ++i) frames[i] = -1;

    int next = 0;        /* índice FIFO: próximo a ser substituído */
    int faults = 0;

    printf("FIFO troca de páginas de memória (capacidade=%d)\n\n", capacity);
    for (i = 0; i < n; ++i) {
        int ref = page_refs[i];
        int found = 0;
        /* verificar se ref já está em frames (hit) */
        for (j = 0; j < capacity; ++j) {
            if (frames[j] == ref) { found = 1; break; }
        }
        if (!found) {
            /* page fault: substituir o frame apontado por 'next' */
            frames[next] = ref;
            next = (next + 1) % capacity; /* circular */
            faults++;
            printf("Ref %d -> FAULT, frames: ", ref);
        } else {
            printf("Ref %d -> HIT  , frames: ", ref);
        }
        /* imprimir estado de frames */
        for (j = 0; j < capacity; ++j) {
            if (frames[j] == -1) printf(" - ");
            else printf("%2d ", frames[j]);
        }
        printf("\n");
    }

    printf("\nTotal de falhas de páginas (page faults): %d\n", faults);
    return 0;
}
