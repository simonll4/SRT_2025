#include <stdio.h>

int main()
{
    float num1, num2;
    int opcion;

    printf("Ingresar el primer número: ");
    scanf("%f", &num1);

    printf("Ingresar el segundo número: ");
    scanf("%f", &num2);

    printf("\nSeleccionar la operación que desea realizar:\n");
    printf("1. Suma\n");
    printf("2. Resta\n");
    printf("3. Multiplicación\n");
    printf("4. División\n");
    printf("Ingrese el número de la opción: ");
    scanf("%d", &opcion);

    switch (opcion)
    {
    case 1:
        printf("Suma: %.2f + %.2f = %.2f\n", num1, num2, num1 + num2);
        break;
    case 2:
        printf("Resta: %.2f - %.2f = %.2f\n", num1, num2, num1 - num2);
        break;
    case 3:
        printf("Multiplicación: %.2f * %.2f = %.2f\n", num1, num2, num1 * num2);
        break;
    case 4:
        if (num2 != 0)
        {
            printf("División: %.2f / %.2f = %.2f\n", num1, num2, num1 / num2);
        }
        else
        {
            printf("Error: No se puede dividir por cero.\n");
        }
        break;
    default:
        printf("Opción no válida. Por favor, seleccione una opción del 1 al 4.\n");
        break;
    }

    return 0;
}