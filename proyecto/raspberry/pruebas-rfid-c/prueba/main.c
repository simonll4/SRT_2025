#include <stdio.h>
#include <unistd.h>
#include <pigpio.h>
#include "rc522.h"

int main()
{
    if (gpioInitialise() < 0)
    {
        printf("Error al inicializar pigpio.\n");
        return 1;
    }

    int spi_handle = spiOpen(0, 500000, 0); // 500 kHz
    if (spi_handle < 0)
    {
        printf("Error al abrir SPI. Código: %d\n", spi_handle);
        gpioTerminate();
        return 1;
    }
    printf("SPI abierto correctamente. Handle: %d\n", spi_handle);

    rc522_init(spi_handle);

    printf("Versión del RC522: 0x%02X\n", rc522_get_version());
    printf("Estado antena: 0x%02X\n", read_register(TxControlReg));
    // Después de rc522_init
    printf("Configuración completada. Verificando registros:\n");
    printf("ModeReg: 0x%02X\n", read_register(ModeReg));
    printf("RFCfgReg: 0x%02X\n", read_register(RFCfgReg));

    printf("Esperando tarjetas...\n");
    uint8_t uid[5];

    while (1) {
        int result = rc522_check_card(uid);
        if (result == MI_OK) {
            printf("\nTarjeta detectada. UID: ");
            for (int i = 0; i < 4; i++) {
                printf("%02X ", uid[i]);
            }
            printf("\n");
            usleep(1000000); // 1 segundo de pausa
        } else {
            printf("."); // Muestra actividad mientras escanea
            fflush(stdout);
        }
        usleep(100000); // 100ms entre intentos
    }
    spiClose(spi_handle);
    gpioTerminate();
    return 0;
}