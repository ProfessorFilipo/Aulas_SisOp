/*******************************************************
***       Exercicio de implementacao de MUTEX        ***
*** o valor final do contador devera ser igual a qt  ***
*** de threads vezes o incremento. Por exemplo:      ***
*** NUM_THREADS = 4, INCREMENTS = 1000               ***
*** contador = 4000                                  ***
********************************************************
*** Prof. Filipo Mor - github.com/ProfessorFilipo    ***
********************************************************/
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>  // para usar usleep()

#define NUM_THREADS 4
#define INCREMENTS 10   // valor menor para não poluir muito a saída

// Variável compartilhada
int contador = 0;

// Mutex para proteger a seção crítica
pthread_mutex_t lock;

void* incrementa(void* arg) 
{
    int id = *((int*) arg); // identifica a thread
    int i;

    for (i = 0; i < INCREMENTS; i++) 
    {
        // Seção crítica
        pthread_mutex_lock(&lock);
        contador++;
        printf("Thread %d incrementou contador para %d\n", id, contador);
        pthread_mutex_unlock(&lock);

        // Simula tempo de processamento
        usleep(100000); // 0,1 segundo
    }

    pthread_exit(NULL);
}

int main() 
{
    pthread_t threads[NUM_THREADS];
    int ids[NUM_THREADS];
    int i;

    // Inicializa o mutex
    if (pthread_mutex_init(&lock, NULL) != 0) 
    {
        printf("Erro ao inicializar o mutex\n");
        return 1;
    }

    // Criação das threads
    for (i = 0; i < NUM_THREADS; i++) 
    {
        ids[i] = i + 1; // identificadores de 1 até NUM_THREADS
        if (pthread_create(&threads[i], NULL, incrementa, &ids[i]) != 0) 
        {
            printf("Erro ao criar a thread %d\n", i + 1);
            return 1;
        }
    }

    // Aguarda as threads terminarem
    for (i = 0; i < NUM_THREADS; i++) 
    {
        pthread_join(threads[i], NULL);
    }

    // Resultado final esperado
    printf("\nValor final do contador: %d (esperado: %d)\n",
           contador, NUM_THREADS * INCREMENTS);

    // Destroi o mutex
    pthread_mutex_destroy(&lock);

    return 0;
}
