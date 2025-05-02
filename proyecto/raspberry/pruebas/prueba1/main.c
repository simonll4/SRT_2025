#include "mfrc522.h"
#include <pigpio.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

void print_hex(const char *label, const uint8_t *data, size_t len) {
    printf("%s: ", label);
    for(size_t i = 0; i < len; i++) {
        printf("%02X ", data[i]);
    }
    printf("\n");
}

void print_text(const uint8_t *data, size_t len) {
    printf("Texto: ");
    for(size_t i = 0; i < len; i++) {
        if(data[i] == 0) break;
        printf("%c", isprint(data[i]) ? data[i] : '.');
    }
    printf("\n");
}

uint8_t read_ultralight(MFRC522 *dev, uint8_t *output) {
    uint8_t page = 4; // Página inicial de datos en Ultralight
    for(int i = 0; i < 16; i += 4, page++) {
        if(MFRC522_Ultralight_Read(dev, page, &output[i]) != MI_OK) {
            return MI_ERR;
        }
    }
    return MI_OK;
}

uint8_t read_classic(MFRC522 *dev, uint8_t *uid, uint8_t *output) {
    uint8_t keyA[6] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
    if(MFRC522_Auth(dev, PICC_AUTHENT1A, 8, keyA, uid) != MI_OK) {
        return MI_ERR;
    }
    uint8_t status = MFRC522_Read(dev, 8, output);
    MFRC522_StopCrypto1(dev);
    return status;
}

int main() {
    if(gpioInitialise() < 0) {
        fprintf(stderr, "Error inicializando pigpio\n");
        return 1;
    }

    MFRC522 dev;
    MFRC522_Init(&dev, 25, 8);

    printf("Acerca un tag RFID al lector...\n");

    while(1) {
        uint8_t tagType[2];
        if(MFRC522_Request(&dev, PICC_REQIDL, tagType) == MI_OK) {
            uint8_t uid[10];
            if(MFRC522_Anticoll(&dev, uid) == MI_OK) {
                uint32_t id = (uid[3] << 24) | (uid[2] << 16) | (uid[1] << 8) | uid[0];
                printf("\nTag detectado UID: %02X%02X%02X%02X\n", uid[0], uid[1], uid[2], uid[3]);
                printf("ID: %lu\n", (unsigned long)id);

                uint8_t data[16] = {0};
                uint8_t success = 0;

                // Intentar como Ultralight primero
                if(tagType[0] == 0x44 || tagType[0] == 0x04) {
                    printf("Tipo: MIFARE Ultralight/NTAG\n");
                    if(read_ultralight(&dev, data) == MI_OK) {
                        success = 1;
                    }
                } 
                // Intentar como Classic
                else if(tagType[0] == 0x08 || tagType[0] == 0x02) {
                    printf("Tipo: MIFARE Classic\n");
                    if(read_classic(&dev, uid, data) == MI_OK) {
                        success = 1;
                    }
                }

                if(success) {
                    print_hex("Datos", data, 16);
                    print_text(data, 16);
                } else {
                    printf("No se pudo leer el tag\n");
                }

                MFRC522_Halt(&dev);
                break;
            }
        }
        gpioDelay(100000);
    }

    gpioTerminate();
    return 0;
}





// #include "mfrc522.h"
// #include <pigpio.h>
// #include <stdio.h>
// #include <string.h>
// #include <time.h>

// #define BLOCK_ADDR 8 // Bloque típico para datos (evitar sector 0)
// #define KEY_DEFAULT {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF} // Clave por defecto

// void write_data_to_tag(MFRC522 *dev, uint8_t *uid, const char *data) {
//     uint8_t keyA[6] = KEY_DEFAULT;
//     uint8_t status;
//     uint8_t buffer[16] = {0};
    
//     // Copiar datos al buffer (máximo 16 bytes)
//     size_t len = strlen(data);
//     if (len > 16) len = 16;
//     memcpy(buffer, data, len);
    
//     printf("Intentando escribir en el tag: %s\n", data);
    
//     // Autenticar
//     status = MFRC522_Auth(dev, PICC_AUTHENT1A, BLOCK_ADDR, keyA, uid);
//     if (status != MI_OK) {
//         printf("Error de autenticación para escritura\n");
//         return;
//     }
    
//     // Escribir datos
//     status = MFRC522_Write(dev, BLOCK_ADDR, buffer);
//     if (status == MI_OK) {
//         printf("Datos escritos correctamente\n");
//     } else {
//         printf("Error al escribir datos\n");
//     }
    
//     MFRC522_StopCrypto1(dev);
// }

// void read_data_from_tag(MFRC522 *dev, uint8_t *uid) {
//     uint8_t keyA[6] = KEY_DEFAULT;
//     uint8_t status;
//     uint8_t data[18] = {0};
    
//     // Primero intentar sin autenticar (para tags más permisivos)
//     status = MFRC522_Read(dev, BLOCK_ADDR, data);
//     if (status == MI_OK) {
//         printf("Lectura sin autenticación:\n");
//     } else {
//         // Si falla, intentar con autenticación
//         status = MFRC522_Auth(dev, PICC_AUTHENT1A, BLOCK_ADDR, keyA, uid);
//         if (status != MI_OK) {
//             printf("Error de autenticación para lectura\n");
//             return;
//         }
        
//         status = MFRC522_Read(dev, BLOCK_ADDR, data);
//         if (status != MI_OK) {
//             printf("Error al leer datos\n");
//             MFRC522_StopCrypto1(dev);
//             return;
//         }
//     }
    
//     // Mostrar datos
//     printf("Datos leídos (HEX): ");
//     for (int i = 0; i < 16; i++) {
//         printf("%02X ", data[i]);
//     }
//     printf("\n");
    
//     printf("Datos leídos (TEXT): %.*s\n", 16, data);
    
//     if (status == MI_OK) {
//         MFRC522_StopCrypto1(dev);
//     }
// }

// int main() {
//     if (gpioInitialise() < 0) {
//         fprintf(stderr, "Error al inicializar pigpio\n");
//         return 1;
//     }

//     MFRC522 dev;
//     MFRC522_Init(&dev, 25, 8); // RST=GPIO25, SS=GPIO8

//     printf("Lector RFID RC522 inicializado\n");
//     printf("Versión del hardware: 0x%02X\n", Read_MFRC522(&dev, VersionReg));
//     printf("Acerca una tarjeta RFID al lector...\n");

//     const char *data_to_write = "HolaMundoRFID!"; // Datos a grabar

//     while (1) {
//         uint8_t tagType[2];
//         uint8_t status = MFRC522_Request(&dev, PICC_REQIDL, tagType);

//         if (status == MI_OK) {
//             uint8_t uid[10] = {0};
//             status = MFRC522_Anticoll(&dev, uid);

//             if (status == MI_OK) {
//                 printf("\nTarjeta detectada UID: %02X%02X%02X%02X\n",
//                        uid[0], uid[1], uid[2], uid[3]);
                
//                 // 1. Primero escribir datos en el tag
//                 write_data_to_tag(&dev, uid, data_to_write);
                
//                 // Pequeña pausa para permitir que el tag se estabilice
//                 gpioDelay(200000); // 200ms
                
//                 // 2. Leer los datos recién escritos
//                 read_data_from_tag(&dev, uid);
                
//                 MFRC522_Halt(&dev);
                
//                 // Salir después de una operación exitosa (opcional)
//                 break;
//             }
//         }

//         gpioDelay(100000); // Esperar 100ms antes del siguiente intento
//     }

//     gpioTerminate();
//     return 0;
// }








// #define ULTRALIGHT_START_PAGE 4
// #define ULTRALIGHT_END_PAGE 15
// #define ULTRALIGHT_DATA_SIZE 16
// #define MAX_RETRIES 5

// void print_tag_type(uint8_t* tagType) {
//     const char* types[] = {
//         [0x44] = "MIFARE Ultralight/NTAG",
//         [0x04] = "MIFARE Ultralight",
//         [0x02] = "MIFARE Classic 1K"
//     };
//     printf("Tipo: %s\n", (tagType[0] < 3) ? types[tagType[0]] : "Desconocido");
// }

// uint8_t ultralight_operation(MFRC522 *dev, uint8_t page, uint8_t* data, uint8_t write) {
//     uint8_t cmd[6] = {write ? 0xA2 : 0x30, page};
//     uint8_t response[4] = {0};
//     uint8_t len = write ? 1 : 4;
    
//     if(write) {
//         memcpy(&cmd[2], data, 4);
//         len = sizeof(cmd);
//     }

//     for(int i = 0; i < MAX_RETRIES; i++) {
//         uint8_t status = MFRC522_ToCard(dev, PCD_TRANSCEIVE, cmd, len, response, &len);
//         if(status == MI_OK && ((write && response[0] == 0x0A) || (!write && len == 4))) {
//             if(!write) memcpy(data, response, 4);
//             return MI_OK;
//         }
//         MFRC522_Reset(dev);
//         gpioDelay(200000);
//     }
//     return MI_ERR;
// }




// #include "mfrc522.h"
// #include <pigpio.h>
// #include <stdio.h>

// int main()
// {
//     if (gpioInitialise() < 0)
//     {
//         fprintf(stderr, "Error al inicializar pigpio\n");
//         return 1;
//     }

//     MFRC522 dev;
//     MFRC522_Init(&dev, 25, 8); // RST=GPIO25, SS=GPIO8

//     printf("Lector RFID RC522 inicializado\n");
//     printf("Versión del hardware: 0x%02X\n", Read_MFRC522(&dev, VersionReg));
//     printf("Acerca una tarjeta RFID al lector...\n");

//     uint8_t keyA[6] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}; // Clave por defecto

//     while (1)
//     {
//         uint8_t tagType[2];
//         uint8_t status = MFRC522_Request(&dev, PICC_REQIDL, tagType);

//         if (status == MI_OK)
//         {
//             uint8_t uid[5];
//             status = MFRC522_Anticoll(&dev, uid);

//             if (status == MI_OK)
//             {
//                 printf("\nTarjeta detectada UID: %02X%02X%02X%02X\n",
//                        uid[0], uid[1], uid[2], uid[3]);
//                 printf("\naacaa: %02X%02X\n",uid[4],uid[5]);

//                 // SimpleMFRC522 de Python usa el bloque 8 por defecto
//                 uint8_t blockAddr = 8;
//                 uint8_t data[18] = {0};

//                 //  intentar  leer  sin  autenticación
//                 status = MFRC522_Read(&dev, blockAddr, data);
//                 // Mostrar datos como texto (hasta el primer null)
//                 printf("Texto almacenado: %s\n", data);
//                 // Mostrar datos en HEX
//                 printf("Datos HEX: ");
//                 for (int i = 0; i < 16; i++)
//                 {
//                     printf("%02X ", data[i]);
//                 }
//                 printf("\n");

//                 // Autenticar
//                 status = MFRC522_Auth(&dev, PICC_AUTHENT1A, blockAddr, keyA, uid);

//                 if (status == MI_OK)
//                 {
//                     // Leer datos
//                     status = MFRC522_Read(&dev, blockAddr, data);

//                     if (status == MI_OK)
//                     {
//                         // Mostrar datos como texto (hasta el primer null)
//                         printf("Texto almacenado: %s\n", data);

//                         // Mostrar datos en HEX
//                         printf("Datos HEX: ");
//                         for (int i = 0; i < 16; i++)
//                         {
//                             printf("%02X ", data[i]);
//                         }
//                         printf("\n");
//                     }
//                     else
//                     {
//                         printf("Error al leer el bloque %d\n", blockAddr);
//                     }

//                     MFRC522_StopCrypto1(&dev);
//                 }
//                 else
//                 {
//                     printf("Error de autenticación\n");
//                 }

//                 MFRC522_Halt(&dev);
//             }
//         }

//         gpioDelay(100000); // Esperar 100ms antes del siguiente intento
//     }

//     gpioTerminate();
//     return 0;
// }

// // #include "mfrc522.h"
// // #include <stdio.h>
// // #include <stdlib.h>
// // #include <pigpio.h>
// // #include <string.h>

// // int main()
// // {
// //     if (gpioInitialise() < 0)
// //     {
// //         fprintf(stderr, "pigpio no pudo inicializarse\n");
// //         return 1;
// //     }

// //     MFRC522 dev;
// //     MFRC522_Init(&dev, 25, 8);
// //     printf("Versión del hardware: 0x%02X\n", Read_MFRC522(&dev, 0x37));
// //     printf("Acerca una tarjeta RFID al lector...\n");

// //     while (1)
// //     {
// //         uint8_t status, tagType[2];
// //         status = MFRC522_Request(&dev, PICC_REQIDL, tagType);
// //         if (status == MI_OK)
// //         {
// //             printf("Tarjeta detectada\n");
// //             uint8_t uid[5];
// //             status = MFRC522_Anticoll(&dev, uid);

// //             printf("ATQA: %02X %02X\n", tagType[0], tagType[1]);

// //             if (status == MI_OK)
// //             {

// //                 uint8_t data[18];
// //                 uint8_t blockToRead = 4; // Bloque típico para datos
// //                 status = MFRC522_Read(&dev, blockToRead, data);
// //                 MFRC522_StopCrypto1(&dev);
// //                 printf("Datos leídos (ASCII): %.*s\n", 16, data);
// //                 printf("Datos leídos (HEX): ");
// //                 for (int i = 0; i < 16; i++)
// //                 {
// //                     printf("%02X ", data[i]);
// //                 }
// //                 printf("\n");

// //                 // uint8_t keys[][6] = {
// //                 //     {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}, // Clave por defecto
// //                 //     {0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5},
// //                 //     {0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7}, // Clave NDEF
// //                 //     {0x4D, 0x3A, 0x99, 0xC3, 0x51, 0xDD},
// //                 //     {0x00, 0x00, 0x00, 0x00, 0x00, 0x00}, // Clave vacía
// //                 //     {0xB0, 0xB1, 0xB2, 0xB3, 0xB4, 0xB5},
// //                 //     {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF},
// //                 //     {0x71, 0x4C, 0x5C, 0x88, 0x6E, 0x97} // Otra clave común
// //                 // };

// //                 // // Prueba con diferentes bloques (evita bloques de sector trailer)
// //                 // uint8_t blocks_to_try[] = {1, 2, 4, 5, 6, 8, 9, 10};

// //                 // int auth_success = 0;

// //                 // for (int k = 0; k < sizeof(keys) / sizeof(keys[0]); k++)
// //                 // {
// //                 //     for (int b = 0; b < sizeof(blocks_to_try) / sizeof(blocks_to_try[0]); b++)
// //                 //     {
// //                 //         printf("Intentando autenticar con clave %d en bloque %d...\n", k, blocks_to_try[b]);

// //                 //         status = MFRC522_Auth(&dev, PICC_AUTHENT1A, blocks_to_try[b], keys[k], uid);
// //                 //         if (status == MI_OK)
// //                 //         {
// //                 //             printf("Autenticación exitosa con clave %d en bloque %d\n", k, blocks_to_try[b]);

// //                 //             uint8_t data[18];
// //                 //             status = MFRC522_Read(&dev, blocks_to_try[b], data);
// //                 //             if (status == MI_OK)
// //                 //             {
// //                 //                 printf("Datos leídos (ASCII): %.*s\n", 16, data);
// //                 //                 printf("Datos leídos (HEX): ");
// //                 //                 for (int i = 0; i < 16; i++)
// //                 //                 {
// //                 //                     printf("%02X ", data[i]);
// //                 //                 }
// //                 //                 printf("\n");
// //                 //                 auth_success = 1;
// //                 //                 break;
// //                 //             }
// //                 //             else
// //                 //             {
// //                 //                 printf("Error al leer el bloque %d\n", blocks_to_try[b]);
// //                 //             }

// //                 //             MFRC522_StopCrypto1(&dev);
// //                 //         }
// //                 //     }
// //                 //     if (auth_success)
// //                 //         break;
// //                 // }

// //                 // if (!auth_success)
// //                 // {
// //                 //     printf("No se pudo autenticar con ninguna clave en ningún bloque accesible\n");
// //                 // }
// //             }

// //             MFRC522_Halt(&dev);
// //             gpioDelay(1500000); // Espera 1.5 segundos antes de leer otra tarjeta
// //         }
// //     }

// //     gpioTerminate();
// //     return 0;
// // }

// // // int main()
// // // {
// // //     if (gpioInitialise() < 0)
// // //     {
// // //         fprintf(stderr, "pigpio no pudo inicializarse\n");
// // //         return 1;
// // //     }

// // //     MFRC522 dev;
// // //     MFRC522_Init(&dev, 25, 8);
// // //     printf("Versión del hardware: 0x%02X\n", Read_MFRC522(&dev, 0x37));
// // //     printf("Acerca una tarjeta RFID al lector...\n");

// // //     while (1)
// // //     {
// // //         uint8_t status, tagType[2];
// // //         status = MFRC522_Request(&dev, PICC_REQIDL, tagType);
// // //         if (status == MI_OK)
// // //         {
// // //             printf("Tarjeta detectada\n");
// // //             uint8_t uid[5];
// // //             status = MFRC522_Anticoll(&dev, uid);
// // //             printf("UID: %02X%02X%02X%02X\n", uid[0], uid[1], uid[2], uid[3]);

// // //             // if (status == MI_OK)
// // //             // {
// // //             //     printf("UID: %02X%02X%02X%02X\n", uid[0], uid[1], uid[2], uid[3]);

// // //             //     // uint8_t keyA[6] = {0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7};
// // //             //     uint8_t keyA[6] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
// // //             //     uint8_t blockAddr = 8; // Bloque usado por SimpleMFRC522 de Python

// // //             //     uint8_t data[18];
// // //             //     // Autenticar antes de leer
// // //             //     status = MFRC522_Auth(&dev, PICC_AUTHENT1A, blockAddr, keyA, uid);
// // //             //     if (status == MI_OK)
// // //             //     {
// // //             //         printf("Autenticación exitosa en el bloque %d\n", blockAddr);

// // //             //         // Añade esto después de la autenticación exitosa
// // //             //         SetBitMask(&dev, Status2Reg, 0x08); // Activa el cifrado

// // //             //         // Antes de MFRC522_StopCrypto1
// // //             //         ClearBitMask(&dev, Status2Reg, 0x08); // Desactiva el cifrado

// // //             //         uint8_t data[18];
// // //             //         status = MFRC522_Read(&dev, blockAddr, data);
// // //             //         if (status == MI_OK)
// // //             //         {
// // //             //             printf("Datos leídos (ASCII): %.*s\n", 16, data);
// // //             //             printf("Datos leídos (HEX): ");
// // //             //             for (int i = 0; i < 16; i++)
// // //             //             {
// // //             //                 printf("%02X ", data[i]);
// // //             //             }
// // //             //             printf("\n");
// // //             //         }
// // //             //         else
// // //             //         {
// // //             //             printf("Error al leer el bloque %d\n", blockAddr);
// // //             //         }

// // //             //         MFRC522_StopCrypto1(&dev);
// // //             //     }
// // //             //     else
// // //             //     {
// // //             //         printf("Error de autenticación en el bloque %d\n", blockAddr);
// // //             //     }
// // //             // }
// // //             gpioDelay(1500000);
// // //         }
// // //     }

// // //     gpioTerminate();
// // //     return 0;
// // // }

// // // int main()
// // // {
// // //     if (gpioInitialise() < 0)
// // //     {
// // //         fprintf(stderr, "pigpio no pudo inicializarse\n");
// // //         return 1;
// // //     }

// // //     MFRC522 dev;
// // //     MFRC522_Init(&dev, 25, 8); // rst_pin = GPIO25, ss_pin = CE0 (GPIO8)

// // //     printf("Acerca una tarjeta RFID al lector...\n");

// // //     while (1)
// // //     {
// // //         uint8_t status, tagType[2];
// // //         status = MFRC522_Request(&dev, PICC_REQIDL, tagType);
// // //         if (status == MI_OK)
// // //         {
// // //             printf("Tarjeta detectada\n");
// // //             uint8_t uid[5];
// // //             status = MFRC522_Anticoll(&dev, uid);
// // //             if (status == MI_OK)
// // //             {
// // //                 printf("UID: %02X%02X%02X%02X\n", uid[0], uid[1], uid[2], uid[3]);

// // //                 uint8_t keyA[6] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
// // //                 // uint8_t blockAddr = 1;
// // //                 // if (MFRC522_Auth(&dev, PICC_AUTHENT1A, blockAddr, keyA, uid) == MI_OK)
// // //                 // {
// // //                 //     printf("Autenticación exitosa en el bloque %d\n", blockAddr);
// // //                 //     uint8_t data[MAX_LEN];
// // //                 //     if (MFRC522_Read(&dev, blockAddr, data) == MI_OK)
// // //                 //     {
// // //                 //         printf("Datos del bloque %d: ", blockAddr);
// // //                 //         for (int i = 0; i < 16; i++)
// // //                 //             printf("%02X ", data[i]);
// // //                 //         printf("\n");
// // //                 //     }
// // //                 //     else
// // //                 //     {
// // //                 //         printf("Error al leer los datos del bloque %d.\n", blockAddr);
// // //                 //     }
// // //                 //     MFRC522_StopCrypto1(&dev);
// // //                 // }
// // //                 uint8_t blockAddr = 8; // SimpleMFRC522 de Python usa bloque 8 por defecto

// // //                 // Y modificar la parte de lectura:
// // //                 uint8_t data[18]; // 16 bytes de datos + 2 bytes CRC
// // //                 if (MFRC522_Read(&dev, blockAddr, data) == MI_OK)
// // //                 {
// // //                     // Imprimir como texto ASCII
// // //                     printf("Datos leídos: %.*s\n", 16, data);

// // //                     // Imprimir como hexadecimal para depuración
// // //                     printf("Hex: ");
// // //                     for (int i = 0; i < 16; i++)
// // //                     {
// // //                         printf("%02X ", data[i]);
// // //                     }
// // //                     printf("\n");
// // //                 }
// // //                 else
// // //                 {
// // //                     printf("Error de autenticación.\n");
// // //                 }
// // //             }
// // //             gpioDelay(1500000); // Delay para evitar múltiples lecturas
// // //         }
// // //     }

// // //     gpioTerminate();
// // //     return 0;
// // // }
