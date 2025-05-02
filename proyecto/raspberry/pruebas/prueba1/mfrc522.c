#include "mfrc522.h"
#include <pigpio.h>
#include <stdio.h>
#include <string.h>

void Write_MFRC522(MFRC522 *dev, uint8_t addr, uint8_t val) {
    gpioWrite(dev->ss_pin, 0);
    uint8_t buffer[2] = {(addr << 1) & 0x7E, val};
    spiWrite(dev->spi_handle, (char *)buffer, 2);
    gpioWrite(dev->ss_pin, 1);
}

uint8_t Read_MFRC522(MFRC522 *dev, uint8_t addr) {
    gpioWrite(dev->ss_pin, 0);
    uint8_t buffer[2] = {((addr << 1) & 0x7E) | 0x80, 0};
    spiXfer(dev->spi_handle, (char *)buffer, (char *)buffer, 2);
    gpioWrite(dev->ss_pin, 1);
    return buffer[1];
}

void SetBitMask(MFRC522 *dev, uint8_t reg, uint8_t mask) {
    uint8_t tmp = Read_MFRC522(dev, reg);
    Write_MFRC522(dev, reg, tmp | mask);
}

void ClearBitMask(MFRC522 *dev, uint8_t reg, uint8_t mask) {
    uint8_t tmp = Read_MFRC522(dev, reg);
    Write_MFRC522(dev, reg, tmp & (~mask));
}

void MFRC522_Reset(MFRC522 *dev) {
    Write_MFRC522(dev, CommandReg, PCD_RESETPHASE);
    gpioDelay(50000); // 50ms delay después del reset
}

void MFRC522_Init(MFRC522 *dev, int rst_pin, int ss_pin) {
    dev->spi_channel = 0;
    dev->rst_pin = rst_pin;
    dev->ss_pin = ss_pin;

    gpioSetMode(dev->rst_pin, PI_OUTPUT);
    gpioWrite(dev->rst_pin, 1);
    gpioDelay(50000); // 50ms delay

    // Configurar SPI a 500kHz para mayor estabilidad
    dev->spi_handle = spiOpen(dev->spi_channel, 500000, 0);
    if (dev->spi_handle < 0) {
        fprintf(stderr, "Error al inicializar SPI\n");
        return;
    }

    MFRC522_Reset(dev);
    
    // Configuración de temporización
    Write_MFRC522(dev, TModeReg, 0x8D);      // Timer Auto
    Write_MFRC522(dev, TPrescalerReg, 0x3E); // TPrescaler
    Write_MFRC522(dev, TReloadRegL, 30);     // Reload timer con 0x3E8 = 1000
    Write_MFRC522(dev, TReloadRegH, 0);
    
    // Configuración RF
    Write_MFRC522(dev, TxASKReg, 0x40);      // 100% ASK
    Write_MFRC522(dev, ModeReg, 0x3D);       // CRC valor inicial 0x6363
    
    // Encender antena
    SetBitMask(dev, TxControlReg, 0x03);
}

uint8_t MFRC522_Request(MFRC522 *dev, uint8_t reqMode, uint8_t *TagType) {
    uint8_t status, backBits;
    Write_MFRC522(dev, BitFramingReg, 0x07); // RxLastBits[2:0]
    TagType[0] = reqMode;
    status = MFRC522_ToCard(dev, PCD_TRANSCEIVE, TagType, 1, TagType, &backBits);
    return (status != MI_OK || backBits != 0x10) ? MI_ERR : MI_OK;
}

uint8_t MFRC522_Anticoll(MFRC522 *dev, uint8_t *serNum) {
    uint8_t status, unLen;
    uint8_t serNumCheck = 0;
    
    Write_MFRC522(dev, BitFramingReg, 0x00); // RxLastBits[2:0]
    serNum[0] = PICC_ANTICOLL;
    serNum[1] = 0x20;
    
    status = MFRC522_ToCard(dev, PCD_TRANSCEIVE, serNum, 2, serNum, &unLen);
    
    if (status == MI_OK) {
        for (uint8_t i = 0; i < 4; i++) {
            serNumCheck ^= serNum[i];
        }
        if (serNumCheck != serNum[4]) {
            status = MI_ERR;
        }
    }
    return status;
}

uint8_t MFRC522_Auth(MFRC522 *dev, uint8_t authMode, uint8_t blockAddr, uint8_t *key, uint8_t *uid) {
    uint8_t buf[12];
    buf[0] = authMode;
    buf[1] = blockAddr;
    memcpy(&buf[2], key, 6);
    memcpy(&buf[8], uid, 4);

    // 3 intentos de autenticación
    for (int i = 0; i < 3; i++) {
        uint8_t status = MFRC522_ToCard(dev, PCD_AUTHENT, buf, 12, buf, NULL);
        if (status == MI_OK) {
            uint8_t status2 = Read_MFRC522(dev, Status2Reg);
            if (status2 & 0x08) { // Bit Crypto1On activo
                return MI_OK;
            }
        }
        gpioDelay(50000); // 50ms entre intentos
    }
    return MI_ERR;
}

uint8_t MFRC522_Read(MFRC522 *dev, uint8_t blockAddr, uint8_t *recvData) {
    uint8_t cmd[4] = {PICC_READ, blockAddr, 0, 0};
    uint8_t backLen = 18;
    
    // Preparar lectura
    Write_MFRC522(dev, CommIrqReg, 0x7F);    // Limpiar flags
    Write_MFRC522(dev, FIFOLevelReg, 0x80);  // Vaciar FIFO
    Write_MFRC522(dev, BitFramingReg, 0x00); // Resetear BitFraming
    
    // Calcular CRC
    MFRC522_CalculateCRC(dev, cmd, 2, &cmd[2]);
    
    // Enviar comando
    uint8_t status = MFRC522_ToCard(dev, PCD_TRANSCEIVE, cmd, 4, recvData, &backLen);
    
    if (status != MI_OK || backLen != 18) {
        return MI_ERR;
    }
    
    // Verificar CRC
    uint8_t crc[2];
    MFRC522_CalculateCRC(dev, recvData, 16, crc);
    if (crc[0] != recvData[16] || crc[1] != recvData[17]) {
        return MI_ERR;
    }
    
    return MI_OK;
}

uint8_t MFRC522_Write(MFRC522 *dev, uint8_t blockAddr, uint8_t *data) {
    uint8_t buffer[18];
    buffer[0] = PICC_WRITE;
    buffer[1] = blockAddr;
    MFRC522_CalculateCRC(dev, buffer, 2, &buffer[2]);

    for (int i = 0; i < 16; i++) {
        buffer[4 + i] = data[i];
    }

    uint8_t backLen = 0;
    uint8_t status = MFRC522_ToCard(dev, PCD_TRANSCEIVE, buffer, 18, buffer, &backLen);

    if (status != MI_OK || backLen != 4 || (buffer[0] & 0x0F) != 0x0A) {
        return MI_ERR;
    }

    return MI_OK;
}

void MFRC522_CalculateCRC(MFRC522 *dev, uint8_t *data, uint8_t len, uint8_t *result) {
    ClearBitMask(dev, DivIrqReg, 0x04);
    SetBitMask(dev, FIFOLevelReg, 0x80);
    
    for (uint8_t i = 0; i < len; i++) {
        Write_MFRC522(dev, FIFODataReg, data[i]);
    }
    
    Write_MFRC522(dev, CommandReg, PCD_CALCCRC);
    
    // Esperar cálculo (máximo 25ms)
    uint16_t i = 25000;
    while (i-- && !(Read_MFRC522(dev, DivIrqReg) & 0x04)) {
        gpioDelay(1);
    }
    
    result[0] = Read_MFRC522(dev, CRCResultRegL);
    result[1] = Read_MFRC522(dev, CRCResultRegH);
}

uint8_t MFRC522_ToCard(MFRC522 *dev, uint8_t command, uint8_t *sendData, uint8_t sendLen,
                      uint8_t *backData, uint8_t *backLen) {
    uint8_t status = MI_ERR;
    uint8_t irqEn = 0x00, waitIRq = 0x00;
    
    // Configurar interrupciones según el comando
    if (command == PCD_AUTHENT) {
        irqEn = 0x12; // IdleIEn, ErrIEn
        waitIRq = 0x10; // IdleIRq
    } else if (command == PCD_TRANSCEIVE) {
        irqEn = 0x77; // TxIEn, RxIEn, IdleIEn, LoAlertIEn, ErrIEn, TimerIEn
        waitIRq = 0x30; // IdleIRq, RxIRq
    }
    
    Write_MFRC522(dev, CommIEnReg, irqEn | 0x80); // Enable interrupts
    ClearBitMask(dev, CommIrqReg, 0x80); // Clear all interrupt bits
    SetBitMask(dev, FIFOLevelReg, 0x80); // Flush FIFO
    
    Write_MFRC522(dev, CommandReg, PCD_IDLE); // Stop any active command
    
    // Escribir datos en FIFO
    for (uint8_t i = 0; i < sendLen; i++) {
        Write_MFRC522(dev, FIFODataReg, sendData[i]);
    }
    
    // Ejecutar comando
    Write_MFRC522(dev, CommandReg, command);
    
    // Activar transmisión si es necesario
    if (command == PCD_TRANSCEIVE) {
        SetBitMask(dev, BitFramingReg, 0x80); // StartSend
    }
    
    // Esperar finalización (máximo 25ms)
    uint16_t i = 25000;
    uint8_t n;
    do {
        n = Read_MFRC522(dev, CommIrqReg);
        gpioDelay(1);
    } while (i-- && !(n & 0x01) && !(n & waitIRq));
    
    // Desactivar StartSend
    if (command == PCD_TRANSCEIVE) {
        ClearBitMask(dev, BitFramingReg, 0x80);
    }
    
    // Verificar resultado
    if (i > 0 && !(Read_MFRC522(dev, ErrorReg) & 0x1B)) {
        status = MI_OK;
        
        if (command == PCD_TRANSCEIVE && backLen != NULL) {
            uint8_t fifoLevel = Read_MFRC522(dev, FIFOLevelReg);
            uint8_t lastBits = Read_MFRC522(dev, ControlReg) & 0x07;
            *backLen = fifoLevel * 8 + lastBits;
            
            // Leer datos recibidos
            for (uint8_t i = 0; i < fifoLevel; i++) {
                backData[i] = Read_MFRC522(dev, FIFODataReg);
            }
        }
    }
    
    return status;
}

void MFRC522_Halt(MFRC522 *dev) {
    uint8_t buffer[4] = {PICC_HALT, 0, 0, 0};
    MFRC522_CalculateCRC(dev, buffer, 2, &buffer[2]);
    MFRC522_ToCard(dev, PCD_TRANSCEIVE, buffer, 4, buffer, NULL);
}

void MFRC522_StopCrypto1(MFRC522 *dev) {
    ClearBitMask(dev, Status2Reg, 0x08); // Clear Crypto1On bit
}







// #include "mfrc522.h"
// #include <pigpio.h>
// #include <stdio.h>
// #include <string.h>

// void Write_MFRC522(MFRC522 *dev, uint8_t addr, uint8_t val) {
//     gpioWrite(dev->ss_pin, 0);
//     uint8_t buffer[2] = {(addr << 1) & 0x7E, val};
//     spiWrite(dev->spi_handle, (char *)buffer, 2);
//     gpioWrite(dev->ss_pin, 1);
// }

// uint8_t Read_MFRC522(MFRC522 *dev, uint8_t addr) {
//     gpioWrite(dev->ss_pin, 0);
//     uint8_t buffer[2] = {((addr << 1) & 0x7E) | 0x80, 0};
//     spiXfer(dev->spi_handle, (char *)buffer, (char *)buffer, 2);
//     gpioWrite(dev->ss_pin, 1);
//     return buffer[1];
// }

// void SetBitMask(MFRC522 *dev, uint8_t reg, uint8_t mask) {
//     uint8_t tmp = Read_MFRC522(dev, reg);
//     Write_MFRC522(dev, reg, tmp | mask);
// }

// void ClearBitMask(MFRC522 *dev, uint8_t reg, uint8_t mask) {
//     uint8_t tmp = Read_MFRC522(dev, reg);
//     Write_MFRC522(dev, reg, tmp & (~mask));
// }

// void MFRC522_Reset(MFRC522 *dev) {
//     Write_MFRC522(dev, CommandReg, PCD_RESETPHASE);
//     gpioDelay(50000); // 50ms delay después del reset
// }

// void MFRC522_Init(MFRC522 *dev, int rst_pin, int ss_pin) {
//     dev->spi_channel = 0;
//     dev->rst_pin = rst_pin;
//     dev->ss_pin = ss_pin;

//     gpioSetMode(dev->rst_pin, PI_OUTPUT);
//     gpioWrite(dev->rst_pin, 1);
//     gpioDelay(50000); // 50ms delay

//     // Configurar SPI a 500kHz para mayor estabilidad
//     dev->spi_handle = spiOpen(dev->spi_channel, 500000, 0);
//     if (dev->spi_handle < 0) {
//         fprintf(stderr, "Error al inicializar SPI\n");
//         return;
//     }

//     MFRC522_Reset(dev);
    
//     // Configuración de temporización
//     Write_MFRC522(dev, TModeReg, 0x8D);      // Timer Auto
//     Write_MFRC522(dev, TPrescalerReg, 0x3E); // TPrescaler
//     Write_MFRC522(dev, TReloadRegL, 30);     // Reload timer con 0x3E8 = 1000
//     Write_MFRC522(dev, TReloadRegH, 0);
    
//     // Configuración RF
//     Write_MFRC522(dev, TxASKReg, 0x40);      // 100% ASK
//     Write_MFRC522(dev, ModeReg, 0x3D);       // CRC valor inicial 0x6363
    
//     // Encender antena
//     SetBitMask(dev, TxControlReg, 0x03);
// }

// uint8_t MFRC522_Request(MFRC522 *dev, uint8_t reqMode, uint8_t *TagType) {
//     uint8_t status, backBits;
//     Write_MFRC522(dev, BitFramingReg, 0x07); // RxLastBits[2:0]
//     TagType[0] = reqMode;
//     status = MFRC522_ToCard(dev, PCD_TRANSCEIVE, TagType, 1, TagType, &backBits);
//     return (status != MI_OK || backBits != 0x10) ? MI_ERR : MI_OK;
// }

// uint8_t MFRC522_Anticoll(MFRC522 *dev, uint8_t *serNum) {
//     uint8_t status, unLen;
//     uint8_t serNumCheck = 0;
    
//     Write_MFRC522(dev, BitFramingReg, 0x00); // RxLastBits[2:0]
//     serNum[0] = PICC_ANTICOLL;
//     serNum[1] = 0x20;
    
//     status = MFRC522_ToCard(dev, PCD_TRANSCEIVE, serNum, 2, serNum, &unLen);
    
//     if (status == MI_OK) {
//         for (uint8_t i = 0; i < 4; i++) {
//             serNumCheck ^= serNum[i];
//         }
//         if (serNumCheck != serNum[4]) {
//             status = MI_ERR;
//         }
//     }
//     return status;
// }

// uint8_t MFRC522_Auth(MFRC522 *dev, uint8_t authMode, uint8_t blockAddr, uint8_t *key, uint8_t *uid) {
//     uint8_t buf[12];
//     buf[0] = authMode;
//     buf[1] = blockAddr;
//     memcpy(&buf[2], key, 6);
//     memcpy(&buf[8], uid, 4);

//     // 3 intentos de autenticación
//     for (int i = 0; i < 3; i++) {
//         uint8_t status = MFRC522_ToCard(dev, PCD_AUTHENT, buf, 12, buf, NULL);
//         if (status == MI_OK) {
//             uint8_t status2 = Read_MFRC522(dev, Status2Reg);
//             if (status2 & 0x08) { // Bit Crypto1On activo
//                 return MI_OK;
//             }
//         }
//         gpioDelay(50000); // 50ms entre intentos
//     }
//     return MI_ERR;
// }

// uint8_t MFRC522_Read(MFRC522 *dev, uint8_t blockAddr, uint8_t *recvData) {
//     uint8_t cmd[4] = {PICC_READ, blockAddr, 0, 0};
//     uint8_t backLen = 18;
    
//     // Preparar lectura
//     Write_MFRC522(dev, CommIrqReg, 0x7F);    // Limpiar flags
//     Write_MFRC522(dev, FIFOLevelReg, 0x80);  // Vaciar FIFO
//     Write_MFRC522(dev, BitFramingReg, 0x00); // Resetear BitFraming
    
//     // Calcular CRC
//     MFRC522_CalculateCRC(dev, cmd, 2, &cmd[2]);
    
//     // Enviar comando
//     uint8_t status = MFRC522_ToCard(dev, PCD_TRANSCEIVE, cmd, 4, recvData, &backLen);
    
//     if (status != MI_OK || backLen != 18) {
//         return MI_ERR;
//     }
    
//     // Verificar CRC
//     uint8_t crc[2];
//     MFRC522_CalculateCRC(dev, recvData, 16, crc);
//     if (crc[0] != recvData[16] || crc[1] != recvData[17]) {
//         return MI_ERR;
//     }
    
//     return MI_OK;
// }

// uint8_t MFRC522_Write(MFRC522 *dev, uint8_t blockAddr, uint8_t *data) {
//     uint8_t buffer[18];
//     buffer[0] = PICC_WRITE;
//     buffer[1] = blockAddr;
//     MFRC522_CalculateCRC(dev, buffer, 2, &buffer[2]);

//     for (int i = 0; i < 16; i++) {
//         buffer[4 + i] = data[i];
//     }

//     uint8_t backLen = 0;
//     uint8_t status = MFRC522_ToCard(dev, PCD_TRANSCEIVE, buffer, 18, buffer, &backLen);

//     if (status != MI_OK || backLen != 4 || (buffer[0] & 0x0F) != 0x0A) {
//         return MI_ERR;
//     }

//     return MI_OK;
// }

// void MFRC522_CalculateCRC(MFRC522 *dev, uint8_t *data, uint8_t len, uint8_t *result) {
//     ClearBitMask(dev, DivIrqReg, 0x04);
//     SetBitMask(dev, FIFOLevelReg, 0x80);
    
//     for (uint8_t i = 0; i < len; i++) {
//         Write_MFRC522(dev, FIFODataReg, data[i]);
//     }
    
//     Write_MFRC522(dev, CommandReg, PCD_CALCCRC);
    
//     // Esperar cálculo (máximo 25ms)
//     uint16_t i = 25000;
//     while (i-- && !(Read_MFRC522(dev, DivIrqReg) & 0x04)) {
//         gpioDelay(1);
//     }
    
//     result[0] = Read_MFRC522(dev, CRCResultRegL);
//     result[1] = Read_MFRC522(dev, CRCResultRegH);
// }

// uint8_t MFRC522_ToCard(MFRC522 *dev, uint8_t command, uint8_t *sendData, uint8_t sendLen,
//                       uint8_t *backData, uint8_t *backLen) {
//     uint8_t status = MI_ERR;
//     uint8_t irqEn = 0x00, waitIRq = 0x00;
    
//     // Configurar interrupciones según el comando
//     if (command == PCD_AUTHENT) {
//         irqEn = 0x12; // IdleIEn, ErrIEn
//         waitIRq = 0x10; // IdleIRq
//     } else if (command == PCD_TRANSCEIVE) {
//         irqEn = 0x77; // TxIEn, RxIEn, IdleIEn, LoAlertIEn, ErrIEn, TimerIEn
//         waitIRq = 0x30; // IdleIRq, RxIRq
//     }
    
//     Write_MFRC522(dev, CommIEnReg, irqEn | 0x80); // Enable interrupts
//     ClearBitMask(dev, CommIrqReg, 0x80); // Clear all interrupt bits
//     SetBitMask(dev, FIFOLevelReg, 0x80); // Flush FIFO
    
//     Write_MFRC522(dev, CommandReg, PCD_IDLE); // Stop any active command
    
//     // Escribir datos en FIFO
//     for (uint8_t i = 0; i < sendLen; i++) {
//         Write_MFRC522(dev, FIFODataReg, sendData[i]);
//     }
    
//     // Ejecutar comando
//     Write_MFRC522(dev, CommandReg, command);
    
//     // Activar transmisión si es necesario
//     if (command == PCD_TRANSCEIVE) {
//         SetBitMask(dev, BitFramingReg, 0x80); // StartSend
//     }
    
//     // Esperar finalización (máximo 25ms)
//     uint16_t i = 25000;
//     uint8_t n;
//     do {
//         n = Read_MFRC522(dev, CommIrqReg);
//         gpioDelay(1);
//     } while (i-- && !(n & 0x01) && !(n & waitIRq));
    
//     // Desactivar StartSend
//     if (command == PCD_TRANSCEIVE) {
//         ClearBitMask(dev, BitFramingReg, 0x80);
//     }
    
//     // Verificar resultado
//     if (i > 0 && !(Read_MFRC522(dev, ErrorReg) & 0x1B)) {
//         status = MI_OK;
        
//         if (command == PCD_TRANSCEIVE && backLen != NULL) {
//             uint8_t fifoLevel = Read_MFRC522(dev, FIFOLevelReg);
//             uint8_t lastBits = Read_MFRC522(dev, ControlReg) & 0x07;
//             *backLen = fifoLevel * 8 + lastBits;
            
//             // Leer datos recibidos
//             for (uint8_t i = 0; i < fifoLevel; i++) {
//                 backData[i] = Read_MFRC522(dev, FIFODataReg);
//             }
//         }
//     }
    
//     return status;
// }

// void MFRC522_Halt(MFRC522 *dev) {
//     uint8_t buffer[4] = {PICC_HALT, 0, 0, 0};
//     MFRC522_CalculateCRC(dev, buffer, 2, &buffer[2]);
//     MFRC522_ToCard(dev, PCD_TRANSCEIVE, buffer, 4, buffer, NULL);
// }

// void MFRC522_StopCrypto1(MFRC522 *dev) {
//     ClearBitMask(dev, Status2Reg, 0x08); // Clear Crypto1On bit
// }





// #include "mfrc522.h"
// #include <pigpio.h>
// #include <stdio.h>
// #include <string.h>
// #include "mfrc522.h"
// #include <stdio.h>

// static void Write_MFRC522(MFRC522 *dev, uint8_t addr, uint8_t val)
// {
//     gpioWrite(dev->ss_pin, 0);
//     uint8_t buffer[2] = {(addr << 1) & 0x7E, val};
//     spiWrite(dev->spi_handle, (char *)buffer, 2);
//     gpioWrite(dev->ss_pin, 1);
// }

// uint8_t Read_MFRC522(MFRC522 *dev, uint8_t addr)
// {
//     gpioWrite(dev->ss_pin, 0);
//     uint8_t buffer[2] = {((addr << 1) & 0x7E) | 0x80, 0};
//     spiXfer(dev->spi_handle, (char *)buffer, (char *)buffer, 2);
//     gpioWrite(dev->ss_pin, 1);
//     return buffer[1];
// }

// void SetBitMask(MFRC522 *dev, uint8_t reg, uint8_t mask)
// {
//     uint8_t tmp = Read_MFRC522(dev, reg);
//     Write_MFRC522(dev, reg, tmp | mask);
// }

// void ClearBitMask(MFRC522 *dev, uint8_t reg, uint8_t mask)
// {
//     uint8_t tmp = Read_MFRC522(dev, reg);
//     Write_MFRC522(dev, reg, tmp & (~mask));
// }

// void MFRC522_Reset(MFRC522 *dev)
// {
//     Write_MFRC522(dev, CommandReg, PCD_RESETPHASE);
// }

// void MFRC522_Init(MFRC522 *dev, int rst_pin, int ss_pin)
// {
//     dev->spi_channel = 0;
//     dev->rst_pin = rst_pin;
//     dev->ss_pin = ss_pin;

//     gpioSetMode(dev->rst_pin, PI_OUTPUT);
//     gpioWrite(dev->rst_pin, 1);
//     time_sleep(0.05);

//     dev->spi_handle = spiOpen(dev->spi_channel, 500000, 0);
//     if (dev->spi_handle < 0)
//     {
//         fprintf(stderr, "No se pudo abrir SPI\n");
//     }

//     MFRC522_Reset(dev);
//     Write_MFRC522(dev, TModeReg, 0x8D);
//     Write_MFRC522(dev, TPrescalerReg, 0x3E);
//     Write_MFRC522(dev, TReloadRegL, 30);
//     Write_MFRC522(dev, TReloadRegH, 0);
//     Write_MFRC522(dev, TxASKReg, 0x40);
//     Write_MFRC522(dev, ModeReg, 0x3D);
//     SetBitMask(dev, TxControlReg, 0x03);
// }

// uint8_t MFRC522_Request(MFRC522 *dev, uint8_t reqMode, uint8_t *TagType)
// {
//     uint8_t status, backBits;
//     Write_MFRC522(dev, BitFramingReg, 0x07);
//     TagType[0] = reqMode;
//     status = MFRC522_ToCard(dev, PCD_TRANSCEIVE, TagType, 1, TagType, &backBits);
//     return (status != MI_OK || backBits != 0x10) ? MI_ERR : MI_OK;
// }

// uint8_t MFRC522_Anticoll(MFRC522 *dev, uint8_t *serNum)
// {
//     uint8_t status, unLen;
//     uint8_t serNumCheck = 0;
//     Write_MFRC522(dev, BitFramingReg, 0x00);
//     serNum[0] = PICC_ANTICOLL;
//     serNum[1] = 0x20;
//     status = MFRC522_ToCard(dev, PCD_TRANSCEIVE, serNum, 2, serNum, &unLen);
//     if (status == MI_OK)
//     {
//         for (uint8_t i = 0; i < 4; i++)
//             serNumCheck ^= serNum[i];
//         if (serNumCheck != serNum[4])
//             status = MI_ERR;
//     }
//     return status;
// }

// uint8_t MFRC522_Read(MFRC522 *dev, uint8_t blockAddr, uint8_t *recvData)
// {
//     // 1. Configuración previa crítica
//     Write_MFRC522(dev, CommIrqReg, 0x7F);    // Limpiar flags de interrupción
//     Write_MFRC522(dev, FIFOLevelReg, 0x80);  // Vaciar buffer FIFO
//     Write_MFRC522(dev, BitFramingReg, 0x00); // Resetear control de bits

//     // 2. Preparar comando de lectura
//     uint8_t cmd[4] = {PICC_READ, blockAddr, 0, 0};
//     MFRC522_CalculateCRC(dev, cmd, 2, &cmd[2]);

//     // 3. Enviar comando con timeout extendido
//     uint8_t backLen = 18;
//     uint8_t status = MI_ERR;

//     for (int i = 0; i < 3; i++)
//     { // 3 intentos
//         status = MFRC522_ToCard(dev, PCD_TRANSCEIVE, cmd, 4, recvData, &backLen);
//         if (status == MI_OK && backLen == 18)
//             break;
//         gpioDelay(50000); // 50ms entre intentos
//     }

//     // 4. Diagnóstico avanzado
//     printf("Status: %d, Bytes: %d, FIFO: %d, Control: 0x%02X, Error: 0x%02X\n",
//            status, backLen,
//            Read_MFRC522(dev, FIFOLevelReg),
//            Read_MFRC522(dev, ControlReg),
//            Read_MFRC522(dev, ErrorReg));

//     return (status == MI_OK && backLen == 18) ? MI_OK : MI_ERR;
// }

// // Función para escribir en el bloque de la tarjeta RFID
// uint8_t MFRC522_Write(MFRC522 *dev, uint8_t blockAddr, uint8_t *data)
// {
//     uint8_t buffer[18];
//     buffer[0] = PICC_WRITE; // Comando de escritura
//     buffer[1] = blockAddr;  // Dirección del bloque
//     MFRC522_CalculateCRC(dev, buffer, 2, &buffer[2]);

//     // Añadir los datos a escribir (16 bytes)
//     for (int i = 0; i < 16; i++)
//     {
//         buffer[4 + i] = data[i];
//     }

//     uint8_t backLen = 0;
//     uint8_t result = MFRC522_ToCard(dev, PCD_TRANSCEIVE, buffer, 18, buffer, &backLen);

//     // Verificamos que la operación haya sido exitosa
//     if (result != MI_OK || backLen != 0x10)
//     {
//         printf("Error al escribir en el bloque %d\n", blockAddr);
//         return MI_ERR;
//     }

//     return MI_OK;
// }

// void MFRC522_Halt(MFRC522 *dev)
// {
//     uint8_t buffer[4] = {PICC_HALT, 0, 0, 0};
//     MFRC522_CalculateCRC(dev, buffer, 2, &buffer[2]);
//     uint8_t unLen;
//     MFRC522_ToCard(dev, PCD_TRANSCEIVE, buffer, 4, buffer, &unLen);
// }
// uint8_t MFRC522_Auth(MFRC522 *dev, uint8_t authMode, uint8_t blockAddr, uint8_t *key, uint8_t *uid)
// {
//     uint8_t buf[12];
//     buf[0] = authMode;
//     buf[1] = blockAddr;
//     for (int i = 0; i < 6; i++)
//         buf[i + 2] = key[i];
//     for (int i = 0; i < 4; i++)
//         buf[i + 8] = uid[i];

//     // Añadir delay para estabilidad
//     gpioDelay(100000); // 100ms

//     uint8_t status = MFRC522_ToCard(dev, PCD_AUTHENT, buf, 12, buf, NULL);

//     // Verificación adicional con reintentos
//     if (status != MI_OK)
//     {
//         // Intentar hasta 3 veces
//         for (int i = 0; i < 3 && status != MI_OK; i++)
//         {
//             gpioDelay(50000); // 50ms entre intentos
//             status = MFRC522_ToCard(dev, PCD_AUTHENT, buf, 12, buf, NULL);
//         }
//     }

//     if (status == MI_OK)
//     {
//         uint8_t status2 = Read_MFRC522(dev, Status2Reg);
//         if (!(status2 & 0x08))
//         {
//             printf("Auth fallida (Status2Reg=0x%02X)\n", status2);

//             // Intenta forzar el bit de crypto si está cerca
//             if (status2 & 0x04)
//             { // Si el bit 2 está activo
//                 SetBitMask(dev, Status2Reg, 0x08);

//                 printf("Forzando bit de crypto...\n");
//                 return MI_OK;
//             }
//             return MI_ERR;
//         }
//     }
//     return status;
// }
// // uint8_t MFRC522_Auth(MFRC522 *dev, uint8_t authMode, uint8_t blockAddr, uint8_t *key, uint8_t *uid)
// // {
// //     uint8_t buf[12];
// //     buf[0] = authMode;
// //     buf[1] = blockAddr;
// //     for (int i = 0; i < 6; i++)
// //         buf[i + 2] = key[i];
// //     for (int i = 0; i < 4; i++)
// //         buf[i + 8] = uid[i];

// //     gpioDelay(50000);
// //     uint8_t status = MFRC522_ToCard(dev, PCD_AUTHENT, buf, 12, buf, NULL);

// //     // Verificación adicional
// //     if (status == MI_OK)
// //     {
// //         uint8_t status2 = Read_MFRC522(dev, Status2Reg);
// //         if (!(status2 & 0x08))
// //         { // Bit 3 (0x08) debe activarse
// //             printf("Auth fallida (Status2Reg=0x%02X)\n", status2);
// //             return MI_ERR;
// //         }
// //     }
// //     return status;
// // }

// void MFRC522_StopCrypto1(MFRC522 *dev)
// {
//     ClearBitMask(dev, Status2Reg, 0x08);
// }

// void MFRC522_CalculateCRC(MFRC522 *dev, uint8_t *data, uint8_t len, uint8_t *result)
// {
//     ClearBitMask(dev, DivIrqReg, 0x04);
//     SetBitMask(dev, FIFOLevelReg, 0x80);
//     for (uint8_t i = 0; i < len; i++)
//         Write_MFRC522(dev, FIFODataReg, data[i]);
//     Write_MFRC522(dev, CommandReg, PCD_CALCCRC);
//     int i = 255;
//     while (i-- && !(Read_MFRC522(dev, DivIrqReg) & 0x04))
//         ;
//     result[0] = Read_MFRC522(dev, CRCResultRegL);
//     result[1] = Read_MFRC522(dev, CRCResultRegH);
// }

// uint8_t MFRC522_ToCard(MFRC522 *dev, uint8_t command, uint8_t *sendData, uint8_t sendLen,
//                        uint8_t *backData, uint8_t *backLen)
// {
//     uint8_t status = MI_ERR;
//     uint8_t irqEn = 0x00, waitIRq = 0x00;
//     if (command == PCD_AUTHENT)
//     {
//         irqEn = 0x12;
//         waitIRq = 0x10;
//     }
//     if (command == PCD_TRANSCEIVE)
//     {
//         irqEn = 0x77;
//         waitIRq = 0x30;
//     }

//     Write_MFRC522(dev, CommIEnReg, irqEn | 0x80);
//     ClearBitMask(dev, CommIrqReg, 0x80);
//     SetBitMask(dev, FIFOLevelReg, 0x80);
//     Write_MFRC522(dev, CommandReg, PCD_IDLE);

//     for (uint8_t i = 0; i < sendLen; i++)
//         Write_MFRC522(dev, FIFODataReg, sendData[i]);

//     Write_MFRC522(dev, CommandReg, command);
//     if (command == PCD_TRANSCEIVE)
//         SetBitMask(dev, BitFramingReg, 0x80);

//     int i = 2000;
//     uint8_t n;
//     do
//     {
//         n = Read_MFRC522(dev, CommIrqReg);
//     } while (i-- && !(n & 0x01) && !(n & waitIRq));

//     ClearBitMask(dev, BitFramingReg, 0x80);

//     if (i && !(Read_MFRC522(dev, ErrorReg) & 0x7B)) // 0x1B
//     {
//         status = MI_OK;
//         if (n & irqEn & 0x01)
//             status = MI_NOTAGERR;

//         if (command == PCD_TRANSCEIVE && backLen != NULL)
//         {
//             uint8_t fifoLevel = Read_MFRC522(dev, FIFOLevelReg);
//             uint8_t lastBits = Read_MFRC522(dev, ControlReg) & 0x07;
//             *backLen = (lastBits) ? (fifoLevel - 1) * 8 + lastBits : fifoLevel * 8;

//             for (uint8_t i = 0; i < fifoLevel; i++)
//                 backData[i] = Read_MFRC522(dev, FIFODataReg);
//         }
//     }
//     return status;
// }
