#include <stdio.h>
#include <stdlib.h>
#include <pigpio.h>

#define SERVO_PIN 18
#define MIN_PULSEWIDTH 500
#define MAX_PULSEWIDTH 2500
#define MIN_ANGLE 0
#define MAX_ANGLE 180

// Función que convierte grados (0 a 180) en ancho de pulso en microsegundos
int grados_a_pulso(int grados)
{
    if (grados < MIN_ANGLE)
        grados = MIN_ANGLE;
    if (grados > MAX_ANGLE)
        grados = MAX_ANGLE;
    return MIN_PULSEWIDTH + (grados * (MAX_PULSEWIDTH - MIN_PULSEWIDTH) / (MAX_ANGLE - MIN_ANGLE));
}

void limpiar_buffer_entrada()
{
    int c;
    while ((c = getchar()) != '\n' && c != EOF)
    {
    }
}

int main()
{
    int grados;
    char opcion;

    // Inicializar la biblioteca pigpio
    if (gpioInitialise() < 0)
    {
        fprintf(stderr, "Error: No se pudo inicializar pigpio. ¿Ejecutaste el programa con sudo?\n");
        return EXIT_FAILURE;
    }

    printf("\nControl de Servo SG90 - Laboratorio de Programación en C\n");
    printf("----------------------------------------------------\n");

    do
    {
        // Solicitar ángulo al usuario con validación
        while (1)
        {
            printf("\nIngrese un ángulo entre %d° y %d° (o 'q' para salir): ", MIN_ANGLE, MAX_ANGLE);

            if (scanf("%d", &grados) != 1)
            {
                // El usuario no ingresó un número
                limpiar_buffer_entrada();
                printf("Entrada no válida. ");
                continue;
            }

            if (grados < MIN_ANGLE || grados > MAX_ANGLE)
            {
                printf("El ángulo debe estar entre %d y %d grados. ", MIN_ANGLE, MAX_ANGLE);
                limpiar_buffer_entrada();
                continue;
            }

            limpiar_buffer_entrada();
            break;
        }

        // Convertir grados a pulso
        int pulso = grados_a_pulso(grados);
        printf("\nConfigurando servo a %d° (%d μs)\n", grados, pulso);
        printf("Presione ENTER para mover el servo...");
        getchar();

        // Mover el servo
        if (gpioServo(SERVO_PIN, pulso) != 0)
        {
            fprintf(stderr, "Error al configurar el servo\n");
        }

        // Esperar a que el servo complete el movimiento
        time_sleep(0.5);

        // Preguntar si desea continuar
        printf("\n¿Desea mover el servo nuevamente? (s/n): ");
        opcion = getchar();
        limpiar_buffer_entrada();

    } while (opcion == 's' || opcion == 'S');

    // Detener señal PWM y liberar recursos
    gpioServo(SERVO_PIN, 0);
    gpioTerminate();

    printf("\nPrograma finalizado. Recursos liberados.\n");
    return EXIT_SUCCESS;
}

// gcc -o servo_control servo_control.c -lpigpio -lrt -lpthread