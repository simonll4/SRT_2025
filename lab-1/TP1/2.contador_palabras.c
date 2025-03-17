#include <stdio.h>
#include <string.h>

int main() {
    char texto[1000];
    int contador = 0;
    int i;

    printf("Ingresar una cadena de texto: ");
    fgets(texto, sizeof(texto), stdin);

    // reeplazar salto de linea por caracter nulo
    if (texto[strlen(texto) - 1] == '\n') {
        texto[strlen(texto) - 1] = '\0';
    }

    for (i = 0; texto[i] != '\0'; i++) {
        if (texto[i] == ' ' && texto[i + 1] != ' ' && texto[i + 1] != '\0') {
            contador++;
        }
    }

    // contar ultima palabra
    if (strlen(texto) > 0) {
        contador++;
    }

    printf("Número de palabras: %d\n", contador);

    return 0;
}