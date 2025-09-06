/******************************************************************************
***              Exemplo de processos pai e filho no linux                  ***
*******************************************************************************
*** Exemplo de fork: pai cria um filho, ambos executam caminhos diferentes. ***
***   O filho faz um pequeno trabalho e encerra com código de saída 42.     ***
***   O pai espera o filho e imprime o status de término.                   ***
*******************************************************************************
*** Prof. Filipo Mor - github.com/ProfessorFilipo                           ***
*******************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

#define CHILD_DONE 42
// 42 eh a resposta para vida, o universo e tudo mais!
// alem disso, 42 esta dentro do intervalo WEXITSTATUS (0..255)
// portanto, eh seguro de usar. Mas poderia ser qualquer coisa
// no intervalo de WEXITSTATUS.

int main(void)
{
    pid_t pid;
    int status;

    printf("Processo original: PID=%d, PPID=%d\n", (int)getpid(), (int)getppid());

    pid = fork();
    if (pid < 0) {
        perror("fork falhou");
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        /* Código do processo filho */
        printf("Filho: PID=%d, PPID=%d -> começando trabalho...\n",
               (int)getpid(), (int)getppid());

        /* Simula algum trabalho */
        for (int i = 1; i <= 5; ++i) {
            printf("Filho: trabalhando (%d/5)\n", i);
            sleep(1);
        }

        printf("Filho: trabalho concluído, saindo com código CHILD_DONE\n");
        _exit(CHILD_DONE); /* usar _exit() no filho é mais seguro que exit() após fork */
    } else {
        /* Código do processo pai */
        printf("Pai: PID=%d, criou filho com PID=%d\n", (int)getpid(), (int)pid);

        /* Aqui o pai pode fazer outra coisa; vamos demonstrar espera bloqueante */
        if (waitpid(pid, &status, 0) == -1) {
            perror("waitpid falhou");
            return EXIT_FAILURE;
        }

        if (WIFEXITED(status)) {
            printf("Pai: filho terminou normalmente com status de saída = %d\n",
                   WEXITSTATUS(status));
        } else if (WIFSIGNALED(status)) {
            printf("Pai: filho foi terminado por sinal = %d\n", WTERMSIG(status));
        } else {
            printf("Pai: filho terminou por outra razão (status = %d)\n", status);
        }

        printf("Pai: finalizando.\n");
    }

    return EXIT_SUCCESS;
}

