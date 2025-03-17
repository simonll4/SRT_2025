#include <stdio.h>
#include <pigpio.h>

#define LED_PIN 19 // Define el pin GPIO donde está conectado el LED

int main()
{
    // Inicializa la librería pigpio
    if (gpioInitialise() < 0)
    {
        fprintf(stderr, "Error al inicializar pigpio\n");
        return 1;
    }

    // Configura el pin del LED como salida
    gpioSetMode(LED_PIN, PI_OUTPUT);

    while (1)
    {
        // Enciende el LED
        gpioWrite(LED_PIN, 1);
        printf("LED_ON\n");

        // Espera 500ms
        gpioDelay(500000); // 500ms en microsegundos

        // Apaga el LED
        gpioWrite(LED_PIN, 0);
        printf("LED_OFF\n");

        // Espera 500ms
        gpioDelay(500000); // 500ms en microsegundos
    }

    // Finaliza la librería pigpio (este código no se alcanzará en este ejemplo)
    gpioTerminate();

    return 0;
}