
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include <string.h>
#include <mqueue.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <pigpio.h>

#define MAX_VEHICULOS 10
#define MAX_MSG_SIZE 256
#define COLA_NOMBRE "/cola_estacionamiento"

// Configuración de pines GPIO
#define LED_VERDE 17      // LED verde compartido
#define LED_ROJO 27       // LED rojo compartido
#define PULSADOR_A 22     // Pulsador entrada A
#define PULSADOR_B 25     // Pulsador entrada B
#define PULSADOR_EGRESO 5 // Pulsador egreso

typedef struct
{
    char patente[10];
    char fecha[11];
    char hora[6];
    char puerta; // 'A' o 'B' para indicar la puerta
} VehiculoInfo;

pthread_mutex_t mutex_contador = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t mutex_leds = PTHREAD_MUTEX_INITIALIZER;
int vehiculos_en_playa = 0;
mqd_t cola_mensajes;

volatile int pulsador_a_presionado = 0;
volatile int pulsador_b_presionado = 0;
volatile int pulsador_egreso_presionado = 0;

// Prototipos de funciones
void actualizar_leds();
void manejar_ingreso(char puerta, int gpio_pulsador, volatile int *flag_pulsador);
void generar_patente(char *patente, char puerta);

// Callback para los pulsadores
void pulsador_a_callback(int gpio, int level, uint32_t tick)
{
    if (level == 1)
        pulsador_a_presionado = 1;
}

void pulsador_b_callback(int gpio, int level, uint32_t tick)
{
    if (level == 1)
        pulsador_b_presionado = 1;
}

void pulsador_egreso_callback(int gpio, int level, uint32_t tick)
{
    if (level == 1)
        pulsador_egreso_presionado = 1;
}

void actualizar_leds()
{
    pthread_mutex_lock(&mutex_leds);
    if (vehiculos_en_playa < MAX_VEHICULOS)
    {
        gpioWrite(LED_VERDE, 1);
        gpioWrite(LED_ROJO, 0);
    }
    else
    {
        gpioWrite(LED_VERDE, 0);
        gpioWrite(LED_ROJO, 1);
    }
    pthread_mutex_unlock(&mutex_leds);
}

void generar_patente(char *patente, char puerta)
{
    // Formato: LetraPuerta + 3 dígitos + AA (ej: A123AA, B456AA)
    snprintf(patente, 10, "%c%dAA", puerta, rand() % 1000);
}

void manejar_ingreso(char puerta, int gpio_pulsador, volatile int *flag_pulsador)
{
    pthread_mutex_lock(&mutex_contador);

    if (vehiculos_en_playa < MAX_VEHICULOS)
    {
        vehiculos_en_playa++;

        // Registrar vehículo
        time_t now = time(NULL);
        struct tm *t = localtime(&now);

        VehiculoInfo info;
        strftime(info.fecha, sizeof(info.fecha), "%d/%m/%y", t);
        strftime(info.hora, sizeof(info.hora), "%H:%M", t);
        info.puerta = puerta;
        generar_patente(info.patente, puerta);

        mq_send(cola_mensajes, (const char *)&info, sizeof(info), 0);

        printf("Ingreso por PUERTA %c: %s. Total: %d/%d\n",
               puerta, info.patente, vehiculos_en_playa, MAX_VEHICULOS);

        actualizar_leds();

        // Feedback visual
        pthread_mutex_lock(&mutex_leds);
        //parpadear_led(LED_VERDE, 2);
        pthread_mutex_unlock(&mutex_leds);
    }
    else
    {
        printf("Playe llena - Ingreso por PUERTA %c denegado\n", puerta);

        actualizar_leds();

        // Feedback visual
        pthread_mutex_lock(&mutex_leds);
        //parpadear_led(LED_ROJO, 3);
        pthread_mutex_unlock(&mutex_leds);
    }

    pthread_mutex_unlock(&mutex_contador);

    // Esperar liberación del pulsador
    while (gpioRead(gpio_pulsador) == 1)
    {
        usleep(10000);
    }
    *flag_pulsador = 0;
}

void *ingreso_A(void *arg)
{
    while (1)
    {
        if (pulsador_a_presionado)
        {
            manejar_ingreso('A', PULSADOR_A, &pulsador_a_presionado);
        }
        usleep(10000);
    }
    return NULL;
}

void *ingreso_B(void *arg)
{
    while (1)
    {
        if (pulsador_b_presionado)
        {
            manejar_ingreso('B', PULSADOR_B, &pulsador_b_presionado);
        }
        usleep(10000);
    }
    return NULL;
}

void *egreso_C(void *arg)
{
    while (1)
    {
        if (pulsador_egreso_presionado)
        {
            pthread_mutex_lock(&mutex_contador);

            if (vehiculos_en_playa > 0)
            {
                vehiculos_en_playa--;
                printf("Egreso por C. Vehículos restantes: %d/%d\n",
                       vehiculos_en_playa, MAX_VEHICULOS);
                actualizar_leds();
            }
            else
            {
                printf("No hay vehículos para egresar\n");
            }

            pthread_mutex_unlock(&mutex_contador);

            while (gpioRead(PULSADOR_EGRESO) == 1)
            {
                usleep(10000);
            }
            pulsador_egreso_presionado = 0;
        }
        usleep(10000);
    }
    return NULL;
}

void *impresor_D(void *arg)
{
    while (1)
    {
        VehiculoInfo info;
        unsigned int prio;

        if (mq_receive(cola_mensajes, (char *)&info, sizeof(info), &prio) != -1)
        {
            printf("\n--- REGISTRO DE INGRESO ---\n");
            printf("PATENTE: %s\n", info.patente);
            printf("FECHA : %s\n", info.fecha);
            printf("HORA:  %s\n", info.hora);
            printf("INGRESO: %c\n", info.puerta);
            printf("--------------------------\n\n");
        }
        usleep(50000);
    }
    return NULL;
}

void configurar_gpio()
{
    // Configurar LEDs como salida
    gpioSetMode(LED_VERDE, PI_OUTPUT);
    gpioSetMode(LED_ROJO, PI_OUTPUT);

    // Configurar pulsadores como entrada con pull-down
    gpioSetMode(PULSADOR_A, PI_INPUT);
    gpioSetPullUpDown(PULSADOR_A, PI_PUD_DOWN);

    gpioSetMode(PULSADOR_B, PI_INPUT);
    gpioSetPullUpDown(PULSADOR_B, PI_PUD_DOWN);

    gpioSetMode(PULSADOR_EGRESO, PI_INPUT);
    gpioSetPullUpDown(PULSADOR_EGRESO, PI_PUD_DOWN);

    // Configurar callbacks
    gpioSetAlertFunc(PULSADOR_A, pulsador_a_callback);
    gpioSetAlertFunc(PULSADOR_B, pulsador_b_callback);
    gpioSetAlertFunc(PULSADOR_EGRESO, pulsador_egreso_callback);

    // Estado inicial de LEDs
    actualizar_leds();
}

int main()
{
    if (gpioInitialise() < 0)
    {
        fprintf(stderr, "Error al inicializar pigpio\n");
        return 1;
    }

    configurar_gpio();

    pthread_t hilo_A, hilo_B, hilo_C, hilo_D;

    // Crear cola de mensajes
    struct mq_attr attr;
    attr.mq_flags = 0;
    attr.mq_maxmsg = 10;
    attr.mq_msgsize = sizeof(VehiculoInfo);
    attr.mq_curmsgs = 0;

    mq_unlink(COLA_NOMBRE);
    cola_mensajes = mq_open(COLA_NOMBRE, O_CREAT | O_RDWR, 0644, &attr);

    if (cola_mensajes == (mqd_t)-1)
    {
        perror("Error al crear la cola de mensajes");
        gpioTerminate();
        exit(EXIT_FAILURE);
    }

    // Crear hilos
    pthread_create(&hilo_A, NULL, ingreso_A, NULL);
    pthread_create(&hilo_B, NULL, ingreso_B, NULL);
    pthread_create(&hilo_C, NULL, egreso_C, NULL);
    pthread_create(&hilo_D, NULL, impresor_D, NULL);

    printf("Sistema de control de estacionamiento iniciado\n");
    printf("Puerta A: GPIO %d\n", PULSADOR_A);
    printf("Puerta B: GPIO %d\n", PULSADOR_B);
    printf("Egreso C: GPIO %d\n", PULSADOR_EGRESO);
    printf("LED Verde: GPIO %d\n", LED_VERDE);
    printf("LED Rojo: GPIO %d\n", LED_ROJO);
    printf("Presione Ctrl+C para salir\n");

    while (1)
    {
        pause();
    }

    // Limpieza
    mq_close(cola_mensajes);
    mq_unlink(COLA_NOMBRE);
    gpioTerminate();

    return 0;
}
