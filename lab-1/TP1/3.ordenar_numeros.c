#include <stdio.h>

// bubble sort
void ordenar(int arr[], int n, int ascendente)
{
    int temp;
    for (int i = 0; i < n - 1; i++)
    {
        for (int j = 0; j < n - i - 1; j++)
        {
            if ((ascendente && arr[j] > arr[j + 1]) || (!ascendente && arr[j] < arr[j + 1]))
            {
                temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

int main()
{
    int n, opcion;

    printf("Ingrese la cantidad de números: ");
    scanf("%d", &n);

    int numeros[n];

    printf("Ingrese los %d números:\n", n);
    for (int i = 0; i < n; i++)
    {
        scanf("%d", &numeros[i]);
    }

    printf("\nSeleccione el tipo de ordenamiento:\n");
    printf("1. Ascendente\n");
    printf("2. Descendente\n");
    printf("Ingrese el número de la opción: ");
    scanf("%d", &opcion);

    if (opcion == 1)
    {
        ordenar(numeros, n, 1);
        printf("Números ordenados de manera ascendente:\n");
    }
    else if (opcion == 2)
    {
        ordenar(numeros, n, 0);
        printf("Números ordenados de manera descendente:\n");
    }
    else
    {
        printf("Opción no válida.\n");
        return 1;
    }

    for (int i = 0; i < n; i++)
    {
        printf("%d ", numeros[i]);
    }
    printf("\n");

    return 0;
}