#include <stdio.h>

int main()
{
    long inputVar;
    short shortVar;
    float floatVar;

    printf("Ingrese un número entero de 16 bits (entre -32768 y 32767): ");
    scanf("%ld", &inputVar);

    if (inputVar < -32768 || inputVar > 32767)
    {
        printf("Error: El número ingresado está fuera del rango permitido.\n");
        return 1;
    }

    shortVar = (short)inputVar;
    floatVar = (float)shortVar;

    printf("El valor entero ingresado es: %d\n", shortVar);
    printf("El valor convertido a punto flotante es: %f\n", floatVar);

    return 0;
}