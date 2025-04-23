#include <stdio.h>
#include <stdlib.h>
#include <pigpio.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>

// ==== Configuración de pines para los LEDs ====
#define LED1_PIN 17
#define LED2_PIN 27
#define LED3_PIN 22

// ==== Temporizaciones de las tareas (en ms) ====
#define TASK1_PERIOD_MS 100
#define TASK2_PERIOD_MS 300
#define TASK3_PERIOD_MS 500

// ==== Periodo del ejecutivo cíclico (en µs) ====
#define EXECUTIVE_PERIOD_US 10000 // 10 ms

// ==== Macros para logs ====
#define DEBUG 1
#if DEBUG
#define LOG(msg, ...) printf(msg, ##__VA_ARGS__)
#else
#define LOG(msg, ...)
#endif

// ==== Variables de estado ====
static unsigned int task1_last_run = 0;
static unsigned int task2_last_run = 0;
static unsigned int task3_last_run = 0;

// ==== Bandera de control para salida segura ====
volatile sig_atomic_t running = 1;

// ==== Manejador de señales para limpieza ====
void handle_sigint(int sig)
{
    // IMPORTANTE: Aquí no llamamos a funciones de pigpio
    // Solo marcamos la bandera de salida
    running = 0;
}

// ==== Inicialización de GPIO ====
void gpio_setup()
{
    // Configurar pines como salidas
    gpioSetMode(LED1_PIN, PI_OUTPUT);
    gpioSetMode(LED2_PIN, PI_OUTPUT);
    gpioSetMode(LED3_PIN, PI_OUTPUT);
    
    // Asegurar que todos los LEDs estén apagados al inicio
    gpioWrite(LED1_PIN, 0);
    gpioWrite(LED2_PIN, 0);
    gpioWrite(LED3_PIN, 0);
}

// ==== Tarea 1: Ejecución cada 100 ms ====
void task1(unsigned int current_time_ms)
{
    static int led_state = 0;

    led_state = !led_state;
    gpioWrite(LED1_PIN, led_state);
    LOG("Tarea 1 ejecutada - Tiempo: %d ms - LED %s\n", current_time_ms, led_state ? "ENCENDIDO" : "APAGADO");
}

// ==== Tarea 2: Ejecución cada 300 ms ====
void task2(unsigned int current_time_ms)
{
    static int led_state = 0;

    led_state = !led_state;
    gpioWrite(LED2_PIN, led_state);
    LOG("Tarea 2 ejecutada - Tiempo: %d ms - LED %s\n", current_time_ms, led_state ? "ENCENDIDO" : "APAGADO");
}

// ==== Tarea 3: Ejecución cada 500 ms ====
void task3(unsigned int current_time_ms)
{
    static int led_state = 0;

    led_state = !led_state;
    gpioWrite(LED3_PIN, led_state);
    LOG("Tarea 3 ejecutada - Tiempo: %d ms - LED %s\n", current_time_ms, led_state ? "ENCENDIDO" : "APAGADO");
}

// ==== Función principal ====
int main()
{
    // Registrar señal Ctrl+C
    // Solo establecemos la bandera - las operaciones GPIO ocurrirán en el bucle principal
    signal(SIGINT, handle_sigint);

    // Inicializar la biblioteca pigpio
    if (gpioInitialise() < 0)
    {
        fprintf(stderr, "Error al inicializar pigpio\n");
        return 1;
    }

    // Configurar pines GPIO
    gpio_setup();

    // Inicializar temporizador
    unsigned int next_tick = gpioTick();
    unsigned int start_time = gpioTick() / 1000; // Tiempo inicial en ms

    LOG("Programa iniciado. Presiona Ctrl+C para salir.\n");

    // ==== SOLUCIÓN CLAVE: Capturar estado actual de los LEDs ====
    int led1_state = 0;
    int led2_state = 0;
    int led3_state = 0;

    while (running)
    {
        unsigned int current_time_us = gpioTick();
        unsigned int current_time_ms = current_time_us / 1000 - start_time;

        // Ejecutar tareas según sus periodos
        if (current_time_ms - task1_last_run >= TASK1_PERIOD_MS)
        {
            task1(current_time_ms);
            task1_last_run = current_time_ms;
            // IMPORTANTE: Capturar el estado actual del LED
            led1_state = gpioRead(LED1_PIN);
        }

        if (current_time_ms - task2_last_run >= TASK2_PERIOD_MS)
        {
            task2(current_time_ms);
            task2_last_run = current_time_ms;
            // IMPORTANTE: Capturar el estado actual del LED
            led2_state = gpioRead(LED2_PIN);
        }

        if (current_time_ms - task3_last_run >= TASK3_PERIOD_MS)
        {
            task3(current_time_ms);
            task3_last_run = current_time_ms;
            // IMPORTANTE: Capturar el estado actual del LED
            led3_state = gpioRead(LED3_PIN);
        }

        // Control del período del ejecutivo cíclico
        next_tick += EXECUTIVE_PERIOD_US;
        int delay = next_tick - gpioTick();

        if (delay > 0)
        {
            gpioDelay(delay);
        }
        else
        {
            LOG("ADVERTENCIA: Período excedido en %d us\n", -delay);
            next_tick = gpioTick();
        }
    }

    // SOLUCIÓN CLAVE: Apagar todos los LEDs explícitamente al salir del bucle
    LOG("Apagando todos los LEDs...\n");
    
    // Garantizar que todos los LEDs estén apagados, independientemente de su estado actual
    gpioWrite(LED1_PIN, 0);
    gpioWrite(LED2_PIN, 0);
    gpioWrite(LED3_PIN, 0);
    
    // Pequeña pausa para asegurar que los cambios de GPIO se completen
    usleep(50000); // 50ms
    
    // Imprimir informe del estado de los LEDs antes de terminar
    LOG("Estado de los LEDs antes de finalizar:\n");
    LOG("LED1: %s -> APAGADO\n", led1_state ? "ENCENDIDO" : "APAGADO");
    LOG("LED2: %s -> APAGADO\n", led2_state ? "ENCENDIDO" : "APAGADO");
    LOG("LED3: %s -> APAGADO\n", led3_state ? "ENCENDIDO" : "APAGADO");
    
    // Terminar la biblioteca pigpio
    gpioTerminate();
    
    LOG("Programa finalizado correctamente\n");
    fflush(stdout);

    return 0;
}