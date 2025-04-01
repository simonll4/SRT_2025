#include <stdio.h>
#include <stdlib.h>
#include <time.h>      
#include <stdbool.h>
#include <unistd.h>
#include <errno.h>
#include <limits.h>

#define NUM_TASKS 3

struct Task {
    int id;
    unsigned long period_ms;
    struct timespec next_run;
};

// Añade ms a un struct timespec
void timespec_add_ms(struct timespec *t, unsigned long ms) {
    t->tv_sec += ms / 1000;
    t->tv_nsec += (ms % 1000) * 1000000;
    if (t->tv_nsec >= 1000000000) {
        t->tv_sec += 1;
        t->tv_nsec -= 1000000000;
    }
}

// Compara dos timespec: a >= b?
bool timespec_ge(const struct timespec *a, const struct timespec *b) {
    if (a->tv_sec > b->tv_sec) return true;
    if (a->tv_sec == b->tv_sec && a->tv_nsec >= b->tv_nsec) return true;
    return false;
}

// Resta dos timespec: a - b
void timespec_sub(struct timespec *result, const struct timespec *a, const struct timespec *b) {
    result->tv_sec = a->tv_sec - b->tv_sec;
    result->tv_nsec = a->tv_nsec - b->tv_nsec;
    if (result->tv_nsec < 0) {
        result->tv_sec -= 1;
        result->tv_nsec += 1000000000;
    }
}

int main() {
    struct timespec start_time;
    clock_gettime(CLOCK_MONOTONIC, &start_time);

    struct Task tasks[NUM_TASKS] = {
        {1, 100, {0}},
        {2, 300, {0}},
        {3, 500, {0}}
    };

    // Inicializar next_run
    for (int i = 0; i < NUM_TASKS; i++) {
        tasks[i].next_run = start_time;
        timespec_add_ms(&tasks[i].next_run, tasks[i].period_ms);
    }

    while (1) {
        struct timespec now;
        clock_gettime(CLOCK_MONOTONIC, &now);

        // Encontrar el próximo tiempo de ejecución más temprano
        struct timespec earliest = {.tv_sec = LONG_MAX, .tv_nsec = 0};
        for (int i = 0; i < NUM_TASKS; i++) {
            if (timespec_ge(&earliest, &tasks[i].next_run)) {
                earliest = tasks[i].next_run;
            }
        }

        // Dormir hasta el próximo evento
        if (clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &earliest, NULL) != 0) {
            perror("clock_nanosleep");
            exit(EXIT_FAILURE);
        }

        // Ejecutar tareas pendientes
        clock_gettime(CLOCK_MONOTONIC, &now);
        for (int i = 0; i < NUM_TASKS; i++) {
            if (timespec_ge(&now, &tasks[i].next_run)) {
                // Calcular tiempo transcurrido
                struct timespec elapsed_ts;
                timespec_sub(&elapsed_ts, &now, &start_time);
                unsigned long elapsed_ms = elapsed_ts.tv_sec * 1000 + elapsed_ts.tv_nsec / 1000000;

                printf("Tarea %d: %lu ms\n", tasks[i].id, elapsed_ms);

                // Programar próxima ejecución
                timespec_add_ms(&tasks[i].next_run, tasks[i].period_ms);
            }
        }
    }

    return 0;
}