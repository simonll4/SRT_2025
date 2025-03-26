#include <stdio.h>

int main()
{
    float floatVar;
    short shortVar;

    printf("Ingrese un número de punto flotante: ");
    scanf("%f", &floatVar);

    if (floatVar > 32767.0f)
    {
        shortVar = 32767;
    }
    else if (floatVar < -32768.0f)
    {
        shortVar = -32768;
    }
    else
    {
        shortVar = (short)floatVar;
    }

    printf("El valor de punto flotante ingresado es: %f\n", floatVar);
    printf("El valor entero short es: %d\n", shortVar);

    return 0;
}