/******************************************************************************
***              Exemplo de múltiplos processos pai e filho no Linux        ***
*******************************************************************************
*** Exemplo de fork em loop: pai cria N filhos, cada um executa um caminho  ***
***   diferente. O pai espera todos e imprime o status de término.          ***
*******************************************************************************
*** Prof. Filipo Mor - github.com/ProfessorFilipo                           ***
*******************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

#define N_CHILDREN 3
// Número de processos filhos que serão criados

#define CHILD_DONE 42
// valor base do código de saída

int main(void)
{
    pid_t pid;
    int status;

    printf("Processo original (PAI): PID=%d, PPID=%d\n", 
           (int)getpid(), (int)getppid());

    for (int i = 0; i < N_CHILDREN; i++) {
        pid = fork();
        if (pid < 0) {
            perror("fork falhou");
            return EXIT_FAILURE;
        }

        if (pid == 0) {
            /* Código do processo filho */
            printf("Filho[%d]: PID=%d, PPID=%d -> começando trabalho...\n",
                   i, (int)getpid(), (int)getppid());

            /* Simula algum trabalho */
            for (int j = 1; j <= 3; ++j) {
                printf("Filho[%d]: trabalhando (%d/3)\n", i, j);
                sleep(1);
            }

            printf("Filho[%d]: trabalho concluído, saindo com código %d\n", 
                   i, CHILD_DONE + i);
            _exit(CHILD_DONE + i); 
        } else {
            /* Código do processo pai (apenas cria e continua o loop) */
            printf("Pai: criou Filho[%d] com PID=%d\n", i, (int)pid);
        }
    }

    /* Pai espera todos os filhos */
    for (int i = 0; i < N_CHILDREN; i++) {
        pid = wait(&status);
        if (pid == -1) {
            perror("wait falhou");
            return EXIT_FAILURE;
        }

        if (WIFEXITED(status)) {
            printf("Pai: filho PID=%d terminou normalmente com status de saída = %d\n",
                   (int)pid, WEXITSTATUS(status));
        } else if (WIFSIGNALED(status)) {
            printf("Pai: filho PID=%d terminou por sinal = %d\n",
                   (int)pid, WTERMSIG(status));
        } else {
            printf("Pai: filho PID=%d terminou por outra razão (status = %d)\n", 
                   (int)pid, status);
        }
    }

    printf("Pai: todos os filhos terminaram. Finalizando.\n");
    return EXIT_SUCCESS;
}
