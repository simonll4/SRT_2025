#include <stdio.h>
#include <stdlib.h>
#include <pigpio.h>
#include <unistd.h>

// ==== Constantes ====
#define BUTTON_PIN 17
#define LED_PIN 18

#define DEBOUNCE_TIME_MS 20
#define EXECUTIVE_PERIOD_US 10000
#define BUTTON_COUNT_PRINT_INTERVAL_US 5000000

// ==== Macros para logs ====
#define DEBUG 1
#if DEBUG
#define LOG(msg, ...) printf(msg, ##__VA_ARGS__)
#else
#define LOG(msg, ...)
#endif

#include <signal.h> // ya incluido con otros headers

void handle_sigint(int sig)
{
    gpioTerminate();
    exit(0);
}

// ==== Estados del botón ====
typedef enum
{
    BUTTON_UP,
    BUTTON_DOWN,
    BUTTON_RISING,
    BUTTON_FALLING
} ButtonState;

// ==== Variables de estado ====
static ButtonState buttonState = BUTTON_UP;

static unsigned int buttonPressedTime = 0;
static unsigned int buttonReleasedTime = 0;
static unsigned int buttonDuration = 0;
static unsigned int buttonPressCount = 0;
static unsigned int lastPrintTime = 0;
static unsigned int lastDebounceTime = 0;

// ==== Inicialización de GPIO ====
void gpio_setup()
{
    gpioWrite(LED_PIN, 0);
}

// ==== Lectura del botón ====
int read_button()
{
    return gpioRead(BUTTON_PIN); // 0 = presionado, 1 = liberado
}

// ==== Tarea A: Manejo de estados del botón con máquina de estados ====
void task_button_state(unsigned int current_time_us)
{
    int current_read = read_button();
    unsigned int current_time_ms = current_time_us / 1000;

    switch (buttonState)
    {
    case BUTTON_UP:
        if (current_read == 0 && (current_time_ms - lastDebounceTime) >= DEBOUNCE_TIME_MS)
        {
            buttonState = BUTTON_FALLING;
            lastDebounceTime = current_time_ms;
        }
        break;

    case BUTTON_FALLING:
        if (current_read == 0)
        {
            buttonState = BUTTON_DOWN;
            buttonPressedTime = current_time_ms;
            LOG("Estado del botón: BUTTON_DOWN\n");
        }
        else
        {
            buttonState = BUTTON_UP;
        }
        break;

    case BUTTON_DOWN:
        if (current_read == 1 && (current_time_ms - lastDebounceTime) >= DEBOUNCE_TIME_MS)
        {
            buttonState = BUTTON_RISING;
            lastDebounceTime = current_time_ms;
        }
        break;

    case BUTTON_RISING:
        if (current_read == 1)
        {
            buttonState = BUTTON_UP;
            buttonReleasedTime = current_time_ms;
            buttonDuration = buttonReleasedTime - buttonPressedTime;
            buttonPressCount++;
            LOG("Estado del botón: BUTTON_UP\n");
            LOG("Botón presionado por %d ms\n", buttonDuration);
        }
        else
        {
            buttonState = BUTTON_DOWN;
        }
        break;
    }
}

// ==== Tarea B: Encendido del LED ====
void task_led_control(unsigned int current_time_us)
{
    static int led_on = 0;
    static unsigned int led_off_time = 0;

    if (buttonState == BUTTON_UP && buttonDuration > 0 && !led_on)
    {
        gpioWrite(LED_PIN, 1);
        led_on = 1;
        led_off_time = current_time_us + (buttonDuration * 1000); // pasar a us
        LOG("LED encendido por %d ms\n", buttonDuration);
        buttonDuration = 0; // reiniciar duración tras usarla
    }

    if (led_on && current_time_us >= led_off_time)
    {
        gpioWrite(LED_PIN, 0);
        led_on = 0;
    }
}

// ==== Tarea C: Mostrar cantidad de pulsaciones cada 5 s ====
void task_button_counter(unsigned int current_time_us)
{
    if (current_time_us - lastPrintTime >= BUTTON_COUNT_PRINT_INTERVAL_US)
    {
        LOG("Total de pulsaciones completas: %d\n", buttonPressCount);
        lastPrintTime = current_time_us;
    }
}

// ==== Main ====
int main()
{

    // Registrar señal Ctrl+C
    signal(SIGINT, handle_sigint);

    if (gpioInitialise() < 0)
    {
        fprintf(stderr, "Error al inicializar pigpio\n");
        return 1;
    }

    gpio_setup();

    unsigned int next_tick = gpioTick();

    while (1)
    {
        unsigned int current_time = gpioTick();

        task_button_state(current_time);
        task_led_control(current_time);
        task_button_counter(current_time);

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

    gpioTerminate();
    return 0;
}

while (1)
{
    task_button_state();
    task_led_control();
    wait_10ms();
}
