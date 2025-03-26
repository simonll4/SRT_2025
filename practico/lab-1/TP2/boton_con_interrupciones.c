#include <stdio.h>
#include <pigpio.h>

#define BOTON 21 // GPIO donde está conectado el botón
#define LED 19   // GPIO donde está conectado el LED

// Función que se ejecuta cuando el botón cambia de estado
void callbackBoton(int gpio, int level, uint32_t tick)
{
    if (level == 1)
    { // Botón presionado (HIGH)
        printf("BOTÓN_PRESIONADO\n");
        gpioWrite(LED, 1); // Enciende LED
    }
    else
    { // Botón liberado (LOW)
        printf("BOTÓN_LIBERADO\n");
        gpioWrite(LED, 0); // Apaga LED
    }
}

int main()
{
    if (gpioInitialise() < 0)
    {
        printf("Error al inicializar pigpio\n");
        return 1;
    }

    gpioSetMode(BOTON, PI_INPUT);
    gpioSetPullUpDown(BOTON, PI_PUD_DOWN); // Activa resistencia Pull-Down interna
    gpioSetMode(LED, PI_OUTPUT);
    gpioWrite(LED, 0); // Asegura que el LED está apagado al inicio

    // Configura la interrupción en el botón (flancos de subida y bajada)
    gpioSetAlertFunc(BOTON, callbackBoton);

    printf("Presiona Ctrl+C para salir\n");
    while (1)
    { // Bucle infinito
        time_sleep(1);
    }

    gpioTerminate();
    return 0;
}
