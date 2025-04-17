#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdbool.h>
#include <unistd.h>
#include <errno.h>
#include <limits.h>
#include <signal.h>
#include <pigpio.h>  // Librería pigpio

#define NUM_TASKS 3
#define GPIO_TASK1 17  // LED para Tarea 1 (GPIO17)
#define GPIO_TASK2 27  // LED para Tarea 2 (GPIO27)
#define GPIO_TASK3 22  // LED para Tarea 3 (GPIO22)

struct Task {
    int id;
    unsigned long period_ms;
    struct timespec next_run;
    int gpio_pin;
    bool led_state;  // Estado del LED (ON/OFF)
};

// Funciones para manejo de tiempo (igual que antes)
void timespec_add_ms(struct timespec *t, unsigned long ms);
bool timespec_ge(const struct timespec *a, const struct timespec *b);
void timespec_sub(struct timespec *result, const struct timespec *a, const struct timespec *b);

// Función para manejar señal de interrupción (Ctrl+C)
volatile sig_atomic_t stop = 0;
void handle_signal(int sig) {
    gpioTerminate();  // Limpiar GPIO
    exit(0);
}

int main() {
    // Inicializar pigpio
    if (gpioInitialise() < 0) {
        fprintf(stderr, "Error al inicializar pigpio\n");
        return 1;
    }

    // Configurar manejo de señales
    signal(SIGINT, handle_signal);

    // Configurar pines GPIO como salidas
    struct Task tasks[NUM_TASKS] = {
        {1, 100, {0}, GPIO_TASK1, false},
        {2, 300, {0}, GPIO_TASK2, false},
        {3, 500, {0}, GPIO_TASK3, false}
    };

    for (int i = 0; i < NUM_TASKS; i++) {
        gpioSetMode(tasks[i].gpio_pin, PI_OUTPUT);  // Modo salida
        gpioWrite(tasks[i].gpio_pin, PI_OFF);       // Iniciar apagado
    }

    struct timespec start_time;
    clock_gettime(CLOCK_MONOTONIC, &start_time);

    // Inicializar next_run
    for (int i = 0; i < NUM_TASKS; i++) {
        tasks[i].next_run = start_time;
        timespec_add_ms(&tasks[i].next_run, tasks[i].period_ms);
    }

    while (!stop) {
        struct timespec now;
        clock_gettime(CLOCK_MONOTONIC, &now);

        // Encontrar el próximo tiempo de ejecución
        struct timespec earliest = {.tv_sec = LONG_MAX, .tv_nsec = 0};
        for (int i = 0; i < NUM_TASKS; i++) {
            if (timespec_ge(&earliest, &tasks[i].next_run)) {
                earliest = tasks[i].next_run;
            }
        }

        // Esperar hasta el próximo evento
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &earliest, NULL);

        // Ejecutar tareas pendientes
        clock_gettime(CLOCK_MONOTONIC, &now);
        for (int i = 0; i < NUM_TASKS; i++) {
            if (timespec_ge(&now, &tasks[i].next_run)) {
                // Toggle LED
                tasks[i].led_state = !tasks[i].led_state;
                gpioWrite(tasks[i].gpio_pin, tasks[i].led_state ? PI_ON : PI_OFF);

                // Calcular tiempo transcurrido
                struct timespec elapsed_ts;
                timespec_sub(&elapsed_ts, &now, &start_time);
                unsigned long elapsed_ms = elapsed_ts.tv_sec * 1000 + elapsed_ts.tv_nsec / 1000000;

                printf("Tarea %d (GPIO %d): %s - %lu ms\n", 
                       tasks[i].id, tasks[i].gpio_pin, 
                       tasks[i].led_state ? "ON" : "OFF", elapsed_ms);

                // Programar próxima ejecución
                timespec_add_ms(&tasks[i].next_run, tasks[i].period_ms);
            }
        }
    }

    gpioTerminate();  // Limpiar GPIO al salir
    return 0;
}

// Implementación de funciones de tiempo (copiar del código anterior)
void timespec_add_ms(struct timespec *t, unsigned long ms) { /* ... */ }
bool timespec_ge(const struct timespec *a, const struct timespec *b) { /* ... */ }
void timespec_sub(struct timespec *result, const struct timespec *a, const struct timespec *b) { /* ... */ }