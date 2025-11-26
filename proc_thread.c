#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <pthread.h>

int global = 0;

void *thread_func(void *arg) {
    int id = *(int *)arg;
    global += 1;
    printf("[THREAD %d] PID=%d, TID=%lu, global=%d\n",
           id, getpid(), pthread_self(), global);
    return NULL;
}

int main(void) {
    printf("[MAIN] PID inicial = %d, global=%d\n", getpid(), global);

    pid_t pid = fork();

    if (pid < 0) {
        perror("fork");
        exit(EXIT_FAILURE);
    }

    if (pid == 0) {  // Processo filho
        global += 10;
        printf("[FILHO] PID=%d, PPID=%d, global=%d\n",
               getpid(), getppid(), global);

        pthread_t t1, t2;
        int id1 = 1, id2 = 2;

        if (pthread_create(&t1, NULL, thread_func, &id1) != 0) {
            perror("pthread_create t1");
            exit(EXIT_FAILURE);
        }

        if (pthread_create(&t2, NULL, thread_func, &id2) != 0) {
            perror("pthread_create t2");
            exit(EXIT_FAILURE);
        }

        pthread_join(t1, NULL);
        pthread_join(t2, NULL);

        printf("[FILHO] global final (processo filho)=%d\n", global);
    } else {         // Processo pai
        sleep(2);    // dá tempo para o filho e suas threads terminarem
        printf("[PAI] PID=%d, filho=%d, global=%d\n",
               getpid(), pid, global);
    }

    return 0;
}

