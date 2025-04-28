#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include <string.h>
#include <semaphore.h>

#define DEFAULT_THRESHOLD 35.0
#define DEFAULT_INTERVAL 1
#define MIN_TEMP 15.0
#define MAX_TEMP 40.0
#define LOG_FILE "temperature_log.txt"

typedef struct
{
    float current_temp;
    float threshold;
    int interval;
    int running;
    pthread_mutex_t mutex;
    sem_t alarm_sem;
} temp_monitor_t;

temp_monitor_t monitor;

// Función para generar una temperatura aleatoria entre MIN_TEMP y MAX_TEMP
float generate_random_temp()
{
    return MIN_TEMP + (float)rand() / (float)(RAND_MAX / (MAX_TEMP - MIN_TEMP));
}

// Manejador de señal para la alarma
void alarm_handler(int sig)
{
    time_t now;
    time(&now);
    char *timestamp = ctime(&now);
    timestamp[strlen(timestamp) - 1] = '\0'; // Eliminar el salto de línea

    pthread_mutex_lock(&monitor.mutex);
    float critical_temp = monitor.current_temp;
    pthread_mutex_unlock(&monitor.mutex);

    FILE *log_file = fopen(LOG_FILE, "a");
    if (log_file)
    {
        fprintf(log_file, "[%s] ALARMA: Temperatura crítica detectada: %.2f°C\n",
                timestamp, critical_temp);
        fclose(log_file);
    }

    printf("[%s] ALARMA: Temperatura crítica detectada: %.2f°C\n",
           timestamp, critical_temp);

    sem_post(&monitor.alarm_sem);
}

// Hilo para leer la temperatura periódicamente
void *temperature_reader(void *arg)
{
    while (monitor.running)
    {
        float temp = generate_random_temp();

        pthread_mutex_lock(&monitor.mutex);
        monitor.current_temp = temp;
        pthread_mutex_unlock(&monitor.mutex);

        // Registrar lectura normal
        time_t now;
        time(&now);
        char *timestamp = ctime(&now);
        timestamp[strlen(timestamp) - 1] = '\0';

        FILE *log_file = fopen(LOG_FILE, "a");
        if (log_file)
        {
            fprintf(log_file, "[%s] Lectura de temperatura: %.2f°C\n",
                    timestamp, temp);
            fclose(log_file);
        }

        // Verificar si supera el umbral
        if (temp > monitor.threshold)
        {
            raise(SIGALRM); // Generar interrupción
        }

        sleep(monitor.interval);
    }
    return NULL;
}

// Hilo para monitorear la temperatura
void *temperature_monitor(void *arg)
{
    while (monitor.running)
    {
        sem_wait(&monitor.alarm_sem); // Esperar por una alarma

        if (!monitor.running)
            break;

        // Aquí podríamos agregar más lógica de manejo de alarmas
        // Por ejemplo, notificaciones adicionales o acciones correctivas
    }
    return NULL;
}

void initialize_monitor(float threshold, int interval)
{
    monitor.current_temp = 0.0;
    monitor.threshold = threshold;
    monitor.interval = interval;
    monitor.running = 1;
    pthread_mutex_init(&monitor.mutex, NULL);
    sem_init(&monitor.alarm_sem, 0, 0);

    // Configurar manejador de señal
    signal(SIGALRM, alarm_handler);
}

void cleanup_monitor()
{
    monitor.running = 0;
    sem_post(&monitor.alarm_sem); // Para despertar al hilo monitor
    pthread_mutex_destroy(&monitor.mutex);
    sem_destroy(&monitor.alarm_sem);
}

int main(int argc, char *argv[])
{
    float threshold = DEFAULT_THRESHOLD;
    int interval = DEFAULT_INTERVAL;

    // Configuración desde argumentos de línea de comandos
    if (argc > 1)
    {
        threshold = atof(argv[1]);
        if (argc > 2)
        {
            interval = atoi(argv[2]);
        }
    }

    printf("Iniciando sistema de monitoreo de temperatura...\n");
    printf("Umbral crítico: %.2f°C\n", threshold);
    printf("Intervalo de lectura: %d segundos\n", interval);

    srand(time(NULL)); // Inicializar semilla para números aleatorios

    initialize_monitor(threshold, interval);

    pthread_t reader_thread, monitor_thread;
    pthread_create(&reader_thread, NULL, temperature_reader, NULL);
    pthread_create(&monitor_thread, NULL, temperature_monitor, NULL);

    printf("Sistema en funcionamiento. Presione Enter para detener...\n");
    getchar();

    cleanup_monitor();

    pthread_join(reader_thread, NULL);
    pthread_join(monitor_thread, NULL);

    printf("Sistema detenido. Registros guardados en %s\n", LOG_FILE);

    return 0;
}