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
#define LOG_FILE "temperature_alarms.log"

typedef struct {
    float current_temp;
    float threshold;
    int interval;
    int running;
    pthread_mutex_t mutex;
} temp_monitor_t;

temp_monitor_t monitor;

// Función que genera temperatura controlada
float generate_controlled_temp(int phase) {
    static int counter = 0;
    counter++;
    
    // Primera fase: temperaturas normales
    if (counter < 15) {
        return MIN_TEMP + (float)rand() / (float)(RAND_MAX / (monitor.threshold - 5 - MIN_TEMP));
    }
    // Segunda fase: se acerca al umbral
    else if (counter < 30) {
        return monitor.threshold - 5 + (float)rand() / (float)(RAND_MAX / 5);
    }
    // Tercera fase: supera el umbral pero nunca el máximo
    else {
        float temp = monitor.threshold + (float)rand() / (float)(RAND_MAX / (MAX_TEMP - monitor.threshold - 1));
        return temp > MAX_TEMP ? MAX_TEMP - 0.1 : temp;
    }
}

// Manejador de alarmas
void alarm_handler(int sig) {
    time_t now;
    time(&now);
    char* timestamp = ctime(&now);
    timestamp[strlen(timestamp)-1] = '\0';
    
    pthread_mutex_lock(&monitor.mutex);
    float critical_temp = monitor.current_temp;
    pthread_mutex_unlock(&monitor.mutex);
    
    // [Registro de eventos] - Sólo para alarmas
    FILE* log_file = fopen(LOG_FILE, "a");
    if (log_file) {
        fprintf(log_file, "[%s] ALARMA: Temperatura %.2f°C (Umbral: %.2f°C)\n", 
                timestamp, critical_temp, monitor.threshold);
        fclose(log_file);
    }
    
    printf("\033[1;31mALARMA: %.2f°C\033[0m\n", critical_temp); // Rojo para alarmas
}

void* temperature_reader(void* arg) {
    int phase = 0;
    while (monitor.running) {
        float temp = generate_controlled_temp(phase);
        phase++;
        
        pthread_mutex_lock(&monitor.mutex);
        monitor.current_temp = temp;
        pthread_mutex_unlock(&monitor.mutex);
        
        // [Mostrar lecturas por pantalla]
        printf("Lectura: %.2f°C\n", temp);
        
        if (temp > monitor.threshold) {
            raise(SIGALRM); // Generar interrupción
        }
        
        sleep(monitor.interval);
    }
    return NULL;
}

void initialize_monitor(float threshold, int interval) {
    monitor.current_temp = 0.0;
    monitor.threshold = threshold;
    monitor.interval = interval;
    monitor.running = 1;
    pthread_mutex_init(&monitor.mutex, NULL);
    signal(SIGALRM, alarm_handler);
}

void cleanup_monitor() {
    monitor.running = 0;
    pthread_mutex_destroy(&monitor.mutex);
}

int main(int argc, char* argv[]) {
    float threshold = DEFAULT_THRESHOLD;
    int interval = DEFAULT_INTERVAL;
    
    if (argc > 1) threshold = atof(argv[1]);
    if (argc > 2) interval = atoi(argv[2]);
    
    printf("=== Sistema de Monitoreo de Temperatura ===\n");
    printf("Umbral: %.2f°C | Intervalo: %ds | Max: %.2f°C\n", 
           threshold, interval, MAX_TEMP);
    printf("Lecturas en pantalla - Alarmas en %s\n", LOG_FILE);
    
    srand(time(NULL));
    initialize_monitor(threshold, interval);
    
    pthread_t reader_thread;
    pthread_create(&reader_thread, NULL, temperature_reader, NULL);
    
    printf("Presione Enter para detener...\n");
    getchar();
    
    cleanup_monitor();
    pthread_join(reader_thread, NULL);
    
    printf("Monitor detenido. Alarmas registradas en %s\n", LOG_FILE);
    return 0;
}
