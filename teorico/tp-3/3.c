#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/types.h>
#include <sys/syscall.h> // Para syscall en algunos sistemas

// Función que ejecutará el hilo
void* funcion_hilo(void* arg) {
    pid_t pid = getpid();          // Obtiene el PID del proceso
    pid_t tid = syscall(SYS_gettid); // Obtiene el TID del hilo (más confiable que pthread_self() para el ID del kernel)
    
    printf("Hilo creado:\n");
    printf("  PID del proceso: %d\n", pid);
    printf("  TID del hilo: %d\n", tid);
    
    return NULL;
}

int main() {
    pthread_t hilo;
    
    printf("Programa principal - PID: %d\n", getpid());
    
    // Crear el hilo
    if (pthread_create(&hilo, NULL, funcion_hilo, NULL) != 0) {
        perror("Error al crear el hilo");
        return EXIT_FAILURE;
    }
    
    // Esperar a que el hilo termine
    pthread_join(hilo, NULL);
    
    return EXIT_SUCCESS;
}