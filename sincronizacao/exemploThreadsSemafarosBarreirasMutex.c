/*****************************************************************
*** Exemplo de sincronização de threads com o uso de SEMAFAROS ***
*** MUTEX e barreiras                                          ***
******************************************************************
*** Prof. Filipo Novo Mór - github.com/ProfessorFilipo         ***
*****************************************************************/

#define _XOPEN_SOURCE 600
// trata-se de uma diretiva de pré-compilação, existente
// na especificaçào X/Open Portability Guide Issue 6 (XPG6)
// para evitar o erro "pthread_barrier_t is undefinied" no VSCode

#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>
#include <time.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>


#define MAXIMO 5
#define MINIMO 1
#define NUM_THREADS 5

// variáveis globais
int contador = 0;
pthread_mutex_t mutex;
sem_t semaforo;
pthread_barrier_t barrier; // Barreira

int SorteiaNumero(int Min, int Max) 
{
    return rand() % (Max - Min + 1) + Min;
}

void *incrementarContador(void *arg) 
{
    int i;
    for (i = 0; i < 100000; i++) 
    {
        // bloqueia o mutex antes de atualizar o contador. caso este esteja 
        // bloqueado por outra thread, aguarda até que o mutex seja liberado.
        if (pthread_mutex_lock(&mutex) != 0) 
        {
            perror("pthread_mutex_lock");
            pthread_exit(NULL);
        }
        
        // atualiza o contador
        contador++;

        // libera o mutex para que outras threads possam seguir sua execução.
        if (pthread_mutex_unlock(&mutex) != 0) 
        {
            perror("pthread_mutex_unlock");
            pthread_exit(NULL);
        }
    }
    printf("Thread %ld: Incremento finalizado. Contador = %d\n", (long)pthread_self(), contador); // Imprime dentro da thread
    pthread_barrier_wait(&barrier); // Espera todas as threads cheguem a este ponto
    pthread_exit(NULL); // termina a thread
}

// simula o acesso a um recurso limitado. 
void *usarRecursoLimitado(void *arg) 
{
    // decrementa o valor do semáfaro. Se o valor for 0, a thread
    // eh bloqueada até que o semáfaro seja incrementado por outra thread.
    // Isso garante que apenas uma thread acesse por vez.
    if (sem_wait(&semaforo) != 0) 
    {
        perror("sem_wait");
        pthread_exit(NULL);
    }

    int sono = SorteiaNumero(MINIMO, MAXIMO);
    printf("Thread %ld: Acessando recurso limitado por %ds...\n", (long)pthread_self(), sono);

    sleep(sono);
    //sleep(1);

    printf("Thread %ld: Liberando recurso limitado apos um sono de %ds...\n", (long)pthread_self(), sono);

    if (sem_post(&semaforo) != 0) 
    {
        perror("sem_post");
        pthread_exit(NULL);
    }

    pthread_exit(NULL);
}

int main() 
{
    srand(time(NULL)); // inicia o gerador de numeros aleatorios

    pthread_t threads[NUM_THREADS]; // cria o vetor de threads
    int i;
    int rc;

    // inicializa o mutex. o argumento NULL indica que o mutex
    // tera atributos padrao.
    if ((rc = pthread_mutex_init(&mutex, NULL)) != 0) 
    {
        fprintf(stderr, "Erro ao inicializar mutex: %s\n", strerror(rc));
        return 1;
    }

    // inicializa o semafaro.
    // o parametro 0 indica que o semafaro eh local (nao compartilhado entre processos)
    // ja o parametro 1, indica o valor inicial do semafaro (1 = recurso disponivel)
    if (sem_init(&semaforo, 0, 1) != 0) 
    {
        perror("sem_init");
        return 1;
    }

    // inicializa a barreira
    // o parametro NULl indica atributos padrao.
    // NUM_THREADS indica a quantidade de threads que deverao aguardar
    // na barreira
    if ((rc = pthread_barrier_init(&barrier, NULL, NUM_THREADS)) != 0) 
    { // Inicializa a barreira
        fprintf(stderr, "Erro ao inicializar barreira: %s\n", strerror(rc));
        return 1;
    }

    printf("Valor INICIAL do contador: %d\n", contador);

    // cria as threads, uma a uma. estas deverao executar a funcao 
    // incrementarContador
    for (i = 0; i < NUM_THREADS; i++) 
    {
        if ((rc = pthread_create(&threads[i], NULL, incrementarContador, NULL)) != 0) 
        {
            fprintf(stderr, "Erro ao criar thread: %s\n", strerror(rc));
            return 1;
        }
    }

    // aguarda as threads finalizarem suas execucoes
    for (i = 0; i < NUM_THREADS; i++) 
    {
        if ((rc = pthread_join(threads[i], NULL)) != 0) 
        {
            fprintf(stderr, "Erro ao aguardar thread: %s\n", strerror(rc));
            return 1;
        }
    }

    pthread_barrier_destroy(&barrier); // Destroi a barreira

    printf("Valor final do contador: %d\n", contador); // Imprime após a barreira

    // cria as threads, uma a uma. estas deverao executar a funcao 
    // usarRecursoLimitado
    for (i = 0; i < NUM_THREADS; i++) 
    {
        if ((rc = pthread_create(&threads[i], NULL, usarRecursoLimitado, NULL)) != 0) 
        {
            fprintf(stderr, "Erro ao criar thread: %s\n", strerror(rc));
            return 1;
        }
    }

    for (i = 0; i < NUM_THREADS; i++) 
    {
        if ((rc = pthread_join(threads[i], NULL)) != 0) {
            fprintf(stderr, "Erro ao aguardar thread: %s\n", strerror(rc));
            return 1;
        }
    }

    if (pthread_mutex_destroy(&mutex) != 0) 
    {
        perror("pthread_mutex_destroy");
        return 1;
    }
    if (sem_destroy(&semaforo) != 0) 
    {
        perror("sem_destroy");
        return 1;
    }

    return 0;
}

