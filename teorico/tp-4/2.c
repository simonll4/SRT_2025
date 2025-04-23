#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

#define NUM_PROCESOS 10

int main() {
    pid_t pid;

    for (int i = 0; i < NUM_PROCESOS; i++) {
        pid = fork();

        if (pid < 0) {
            perror("Error al crear el proceso hijo");
            exit(1);
        } else if (pid == 0) {
            // Código del hijo
            printf("Hijo #%d - PID: %d, PPID: %d\n", i + 1, getpid(), getppid());
            sleep(5);  // Para que el pstree los pueda mostrar activos
            exit(0);   // Termina el hijo
        }
        // El padre continúa para crear más hijos
    }

    // Pequeña pausa para asegurarnos de que los hijos están vivos antes de mostrar pstree
    sleep(1);

    // Mostrar jerarquía de procesos con pstree
    printf("\n=== Jerarquía de procesos (pstree) ===\n");
    char comando[100];
    snprintf(comando, sizeof(comando), "pstree -p %d", getpid());
    system(comando);
    printf("======================================\n\n");

    // Esperar a que todos los hijos terminen
    for (int i = 0; i < NUM_PROCESOS; i++) {
        wait(NULL);
    }

    printf("Todos los hijos han terminado.\n");
    return 0;
}
