#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <string.h>
#include <time.h>
#include <sys/wait.h>
#include <signal.h>
#include <pigpio.h>

#define SHM_NAME "/memcompartida"
#define BUTTON_GPIO 17
#define LED_GPIO 27

typedef struct {
    char nombre[20];
    char fecha_hora[30];
    unsigned int tiempo_ms;
} Datos;

void procesoA(Datos *datos) {
    strcpy(datos->nombre, "BOTON 1");

    while (1) {
        while (gpioRead(BUTTON_GPIO) == 1) usleep(1000);  // espera presión
        struct timespec inicio, fin;
        clock_gettime(CLOCK_MONOTONIC, &inicio);

        while (gpioRead(BUTTON_GPIO) == 0) usleep(1000);  // espera suelta
        clock_gettime(CLOCK_MONOTONIC, &fin);

        unsigned int tiempo = (fin.tv_sec - inicio.tv_sec) * 1000 +
                              (fin.tv_nsec - inicio.tv_nsec) / 1000000;
        datos->tiempo_ms = tiempo;

        time_t now = time(NULL);
        struct tm *t = localtime(&now);
        strftime(datos->fecha_hora, sizeof(datos->fecha_hora), "%H:%M %d/%m/%Y", t);

        printf("Registrado: %s - %s - %u ms\n", datos->nombre, datos->fecha_hora, datos->tiempo_ms);
        sleep(1);  // evitar rebotes
    }
}

void procesoB(Datos *datos) {
    unsigned int periodo_ms = 1000;

    while (1) {
        if (datos->tiempo_ms != periodo_ms && datos->tiempo_ms > 0) {
            periodo_ms = datos->tiempo_ms;
            printf("nombre : %s\n", datos->nombre);
            printf("hora y fecha: %s\n", datos->fecha_hora);
            printf("tiempo pulsado: %u ms.\n", datos->tiempo_ms);
        }

        gpioWrite(LED_GPIO, 1);
        usleep(periodo_ms * 1000 / 2);
        gpioWrite(LED_GPIO, 0);
        usleep(periodo_ms * 1000 / 2);
    }
}

int main() {
    if (gpioInitialise() < 0) {
        fprintf(stderr, "No se pudo iniciar pigpio\n");
        return 1;
    }

    gpioSetMode(BUTTON_GPIO, PI_INPUT);
    gpioSetPullUpDown(BUTTON_GPIO, PI_PUD_UP);
    gpioSetMode(LED_GPIO, PI_OUTPUT);

    // Crear memoria compartida
    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    ftruncate(shm_fd, sizeof(Datos));
    Datos *datos = mmap(0, sizeof(Datos), PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    memset(datos, 0, sizeof(Datos)); // Inicializa la memoria

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return 1;
    } else if (pid == 0) {
        // Proceso hijo: proceso B
        procesoB(datos);
    } else {
        // Proceso padre: proceso A
        procesoA(datos);
    }

    // Nunca se debería llegar aquí
    gpioTerminate();
    return 0;
}
