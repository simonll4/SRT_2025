#include <stdio.h>
#include <time.h>   // Para funciones de tiempo
#include <unistd.h> // Para sleep()

// Función para mostrar la hora actual en formato HH:MM:SS
void relojDigital()
{
    while (1)
    {
        time_t ahora;
        struct tm *infoTiempo;
        char buffer[80];

        // Obtener la hora actual
        time(&ahora);
        infoTiempo = localtime(&ahora);

        // Formatear la hora como HH:MM:SS
        strftime(buffer, sizeof(buffer), "%H:%M:%S", infoTiempo);

        // Mostrar la hora actual
        printf("Reloj Digital: %s\r", buffer);
        fflush(stdout); // Limpiar el buffer de salida para actualizar la misma línea

        sleep(1); // Esperar 1 segundo
    }
}

// Función para implementar un cronómetro
void cronometro()
{
    int segundos = 0;
    while (1)
    {
        // Mostrar el tiempo transcurrido en formato HH:MM:SS
        printf("Cronómetro: %02d:%02d:%02d\r", segundos / 3600, (segundos % 3600) / 60, segundos % 60);
        fflush(stdout);

        sleep(1);
        segundos++;
    }
}

int main()
{
    int opcion;

    printf("Seleccione una opción:\n");
    printf("1. Reloj Digital\n");
    printf("2. Cronómetro\n");
    printf("Ingrese el número de la opción: ");
    scanf("%d", &opcion);

    if (opcion == 1)
    {
        printf("\nReloj Digital (Presione Ctrl+C para salir):\n");
        relojDigital();
    }
    else if (opcion == 2)
    {
        printf("\nCronómetro (Presione Ctrl+C para salir):\n");
        cronometro();
    }
    else
    {
        printf("Opción no válida.\n");
    }

    return 0;
}