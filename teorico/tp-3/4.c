#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/types.h>

#define NUM_THREADS 10

void* print_tid(void* arg) {
    pid_t tid = syscall(SYS_gettid);
    printf("Hola desde el hilo con TID (a nivel sistema): %d\n", tid);
    return NULL;
}

int main() {
    pthread_t threads[NUM_THREADS];

    for (int i = 0; i < NUM_THREADS; i++) {
        if (pthread_create(&threads[i], NULL, print_tid, NULL) != 0) {
            perror("Error al crear el hilo");
            return 1;
        }
    }

    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    return 0;
}
