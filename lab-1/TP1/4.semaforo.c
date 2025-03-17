#include <stdio.h>
#include <unistd.h> 
#include <stdbool.h> 
#include <pthread.h> 

#define TIEMPO_VERDE 5
#define TIEMPO_AMARILLO 2
#define TIEMPO_ROJO 5
#define TIEMPO_CRUCE_PEATONAL 5

bool botonPresionado = false;

void* semaforo(void* arg) {
    while (1) {

        printf("Verde.\n");
        sleep(TIEMPO_VERDE);

        printf("Amarillo.\n");
        sleep(TIEMPO_AMARILLO);

        printf("Rojo.\n");
        sleep(TIEMPO_ROJO);

        if (botonPresionado) {
            printf("Cruce peatonal.\n");
            sleep(TIEMPO_CRUCE_PEATONAL);
            printf("Fin del cruce peatonal.\n");
            botonPresionado = false;
        }
    }
    return NULL;
}

void* escucharBoton(void* arg) {
    char input;
    while (1) {
        if (scanf(" %c", &input) == 1) {
            if (input == 'b') {
                botonPresionado = true;
                printf("Botón de cruce peatonal presionado.\n");
            } else if (input == 'q') {
                printf("Saliendo del simulador...\n");
                return NULL;
            }
        }
    }
    return NULL;
}

int main() {
    pthread_t hiloSemaforo, hiloBoton;

    printf("Simulador de semáforo\n");
    printf("Presione 'b' en cualquier momento para simular el botón de cruce peatonal.\n");
    printf("Presione 'q' para salir.\n");

    pthread_create(&hiloSemaforo, NULL, semaforo, NULL);
    pthread_create(&hiloBoton, NULL, escucharBoton, NULL);

    // Esperar a que el hilo del botón termine (cuando el usuario presione 'q')
    pthread_join(hiloBoton, NULL);

    // Cancelar el hilo del semáforo antes de salir
    pthread_cancel(hiloSemaforo);

    return 0;
}