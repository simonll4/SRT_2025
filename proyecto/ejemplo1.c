#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <wiringPi.h>
#include <wiringPiSPI.h>
#include <rc522.h>

#define SPI_CHANNEL 0
#define SPI_SPEED 1000000
#define RST_PIN 25

int main(void) {
    wiringPiSetup();
    
    // Inicializar el módulo RC522
    if (rc522_init(SPI_CHANNEL, RST_PIN, SPI_SPEED)) {
        printf("Error al inicializar el módulo RC522\n");
        return 1;
    }
    
    printf("Sistema de lectura RFID/NFC\n");
    printf("Coloque una tarjeta o llavero cerca del lector...\n");
    
    while (1) {
        // Verificar si hay una tarjeta presente
        if (rc522_check(0) == 0) {
            // Obtener el UID de la tarjeta
            unsigned char uid[10];
            unsigned char uidSize = sizeof(uid);
            
            if (rc522_get_id(uid, &uidSize) == 0) {
                printf("Tarjeta detectada - UID: ");
                
                // Imprimir el UID en hexadecimal
                for (int i = 0; i < uidSize; i++) {
                    printf("%02X", uid[i]);
                    if (i < uidSize - 1) {
                        printf(":");
                    }
                }
                printf("\n");
                
                // Pequeña pausa para evitar múltiples lecturas
                delay(1000);
            }
        }
        delay(100);
    }
    
    return 0;
}