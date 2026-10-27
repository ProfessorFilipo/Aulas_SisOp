/*******************************************************
*** Gestao de Entrada e Saida - topico 13.4.6        ***
*** Tenta executar, em modo usuario, uma instrucao   ***
*** que DESABILITA AS INTERRUPCOES:                  ***
***   x86 (Intel/AMD) ......... CLI                  ***
***   ARM64 (Apple Silicon) ... MSR DAIFSet, #2      ***
*** O processador recusa e o kernel encerra o        ***
*** programa com um sinal (SIGSEGV ou SIGILL).       ***
*** Compilar: cc privilegiada.c -o privilegiada      ***
********************************************************
*** Prof. Filipo Novo Mor - filipomor.com            ***
*** github.com/ProfessorFilipo                       ***
********************************************************/
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

static void tratador(int sig) {
    const char *msg =
        sig == SIGILL  ? "  -> Bloqueado! O kernel enviou SIGILL (instrucao ilegal em modo usuario).\n" :
        sig == SIGSEGV ? "  -> Bloqueado! O kernel enviou SIGSEGV (violacao de protecao).\n" :
                         "  -> Bloqueado! O kernel enviou SIGBUS.\n";
    write(STDOUT_FILENO, msg, strlen(msg));
    _exit(1);
}

int main(void) {
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = tratador;
    sigaction(SIGILL, &sa, NULL);
    sigaction(SIGSEGV, &sa, NULL);
    sigaction(SIGBUS, &sa, NULL);

    printf("Tentando DESABILITAR AS INTERRUPCOES a partir de um programa comum...\n");
#if defined(__x86_64__) || defined(__i386__)
    printf("  arquitetura x86: instrucao CLI\n");
    fflush(stdout);
    __asm__ volatile("cli");
#elif defined(__aarch64__) || defined(__arm64__)
    printf("  arquitetura ARM64: instrucao MSR DAIFSet, #2\n");
    fflush(stdout);
    __asm__ volatile("msr daifset, #2");
#else
    printf("  arquitetura nao suportada por esta demo\n");
    return 2;
#endif
    printf("  Conseguiu?! (isso nao deveria acontecer)\n");
    return 0;
}
