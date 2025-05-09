#ifndef MFRC522_H
#define MFRC522_H

#include <stdint.h>

#define MAX_LEN 16
#define MI_OK 0
#define MI_NOTAGERR 1
#define MI_ERR 2

// Comandos PCD
#define PCD_IDLE 0x00
#define PCD_AUTHENT 0x0E
#define PCD_TRANSCEIVE 0x0C
#define PCD_RESETPHASE 0x0F
#define PCD_CALCCRC 0x03

// Comandos PICC
#define PICC_REQIDL 0x26
#define PICC_ANTICOLL 0x93
#define PICC_SELECT 0x93
#define PICC_AUTHENT1A 0x60
#define PICC_AUTHENT1B 0x61
#define PICC_READ 0x30
#define PICC_WRITE 0xA0
#define PICC_HALT 0x50

// Registros MFRC522
#define CommandReg 0x01
#define CommIEnReg 0x02
#define CommIrqReg 0x04
#define DivIrqReg 0x05
#define ErrorReg 0x06
#define Status1Reg 0x07
#define Status2Reg 0x08
#define FIFODataReg 0x09
#define FIFOLevelReg 0x0A
#define ControlReg 0x0C
#define BitFramingReg 0x0D
#define ModeReg 0x11
#define TxControlReg 0x14
#define TxASKReg 0x15
#define CRCResultRegH 0x21
#define CRCResultRegL 0x22
#define TModeReg 0x2A
#define TPrescalerReg 0x2B
#define TReloadRegH 0x2C
#define TReloadRegL 0x2D
#define VersionReg 0x37

typedef struct {
    int spi_channel;
    int spi_handle;
    int rst_pin;
    int ss_pin;
} MFRC522;

// Prototipos de funciones
void MFRC522_Init(MFRC522 *dev, int rst_pin, int ss_pin);
void MFRC522_Reset(MFRC522 *dev);
uint8_t MFRC522_Request(MFRC522 *dev, uint8_t reqMode, uint8_t *TagType);
uint8_t MFRC522_Anticoll(MFRC522 *dev, uint8_t *serNum);
uint8_t MFRC522_Auth(MFRC522 *dev, uint8_t authMode, uint8_t blockAddr, uint8_t *key, uint8_t *uid);
uint8_t MFRC522_Read(MFRC522 *dev, uint8_t blockAddr, uint8_t *recvData);
uint8_t MFRC522_Write(MFRC522 *dev, uint8_t blockAddr, uint8_t *data);
void MFRC522_Halt(MFRC522 *dev);
void MFRC522_StopCrypto1(MFRC522 *dev);
void MFRC522_CalculateCRC(MFRC522 *dev, uint8_t *data, uint8_t len, uint8_t *result);
uint8_t MFRC522_ToCard(MFRC522 *dev, uint8_t command, uint8_t *sendData, uint8_t sendLen,
                      uint8_t *backData, uint8_t *backLen);
uint8_t Read_MFRC522(MFRC522 *dev, uint8_t addr);
void Write_MFRC522(MFRC522 *dev, uint8_t addr, uint8_t val);
void SetBitMask(MFRC522 *dev, uint8_t reg, uint8_t mask);
void ClearBitMask(MFRC522 *dev, uint8_t reg, uint8_t mask);
void print_tag_type(uint8_t* tagType);  // Añadido este prototipo


uint8_t MFRC522_Ultralight_Read(MFRC522 *dev, uint8_t page, uint8_t *buffer);
uint8_t MFRC522_Ultralight_Write(MFRC522 *dev, uint8_t page, uint8_t *data);
#endif


// #ifndef MFRC522_H
// #define MFRC522_H

// #include <stdint.h>

// #define MAX_LEN 16
// #define MI_OK 0
// #define MI_NOTAGERR 1
// #define MI_ERR 2

// // Comandos PCD
// #define PCD_IDLE 0x00
// #define PCD_AUTHENT 0x0E
// #define PCD_TRANSCEIVE 0x0C
// #define PCD_RESETPHASE 0x0F
// #define PCD_CALCCRC 0x03

// // Comandos PICC
// #define PICC_REQIDL 0x26
// #define PICC_ANTICOLL 0x93
// #define PICC_SELECT 0x93
// #define PICC_AUTHENT1A 0x60
// #define PICC_AUTHENT1B 0x61
// #define PICC_READ 0x30
// #define PICC_WRITE 0xA0
// #define PICC_HALT 0x50

// // Registros MFRC522
// #define CommandReg 0x01
// #define CommIEnReg 0x02
// #define CommIrqReg 0x04
// #define DivIrqReg 0x05
// #define ErrorReg 0x06
// #define Status1Reg 0x07
// #define Status2Reg 0x08
// #define FIFODataReg 0x09
// #define FIFOLevelReg 0x0A
// #define ControlReg 0x0C
// #define BitFramingReg 0x0D
// #define ModeReg 0x11
// #define TxControlReg 0x14
// #define TxASKReg 0x15
// #define CRCResultRegH 0x21
// #define CRCResultRegL 0x22
// #define TModeReg 0x2A
// #define TPrescalerReg 0x2B
// #define TReloadRegH 0x2C
// #define TReloadRegL 0x2D
// #define VersionReg 0x37

// typedef struct {
//     int spi_channel;
//     int spi_handle;
//     int rst_pin;
//     int ss_pin;
// } MFRC522;

// // Prototipos de funciones
// void MFRC522_Init(MFRC522 *dev, int rst_pin, int ss_pin);
// void MFRC522_Reset(MFRC522 *dev);
// uint8_t MFRC522_Request(MFRC522 *dev, uint8_t reqMode, uint8_t *TagType);
// uint8_t MFRC522_Anticoll(MFRC522 *dev, uint8_t *serNum);
// uint8_t MFRC522_Auth(MFRC522 *dev, uint8_t authMode, uint8_t blockAddr, uint8_t *key, uint8_t *uid);
// uint8_t MFRC522_Read(MFRC522 *dev, uint8_t blockAddr, uint8_t *recvData);
// uint8_t MFRC522_Write(MFRC522 *dev, uint8_t blockAddr, uint8_t *data);
// void MFRC522_Halt(MFRC522 *dev);
// void MFRC522_StopCrypto1(MFRC522 *dev);
// void MFRC522_CalculateCRC(MFRC522 *dev, uint8_t *data, uint8_t len, uint8_t *result);
// uint8_t MFRC522_ToCard(MFRC522 *dev, uint8_t command, uint8_t *sendData, uint8_t sendLen,
//                       uint8_t *backData, uint8_t *backLen);
// uint8_t Read_MFRC522(MFRC522 *dev, uint8_t addr);
// void Write_MFRC522(MFRC522 *dev, uint8_t addr, uint8_t val);
// void SetBitMask(MFRC522 *dev, uint8_t reg, uint8_t mask);
// void ClearBitMask(MFRC522 *dev, uint8_t reg, uint8_t mask);

// #endif

// // #ifndef MFRC522_H
// // #define MFRC522_H

// // #include <stdint.h>

// // #define MAX_LEN 16
// // #define MI_OK 0
// // #define MI_NOTAGERR 1
// // #define MI_ERR 2

// // // Comandos PCD
// // #define PCD_IDLE 0x00
// // #define PCD_AUTHENT 0x0E
// // #define PCD_TRANSCEIVE 0x0C
// // #define PCD_RESETPHASE 0x0F
// // #define PCD_CALCCRC 0x03

// // // Comandos PICC
// // #define PICC_REQIDL 0x26
// // #define PICC_ANTICOLL 0x93
// // #define PICC_SELECT 0x93
// // #define PICC_AUTHENT1A 0x60
// // #define PICC_AUTHENT1B 0x61
// // #define PICC_READ 0x30
// // #define PICC_WRITE 0xA0
// // #define PICC_HALT 0x50

// // // Registros MFRC522
// // #define CommandReg 0x01
// // #define CommIEnReg 0x02
// // #define CommIrqReg 0x04
// // #define DivIrqReg 0x05
// // #define ErrorReg 0x06
// // #define Status1Reg 0x07
// // #define Status2Reg 0x08
// // #define FIFODataReg 0x09
// // #define FIFOLevelReg 0x0A
// // #define ControlReg 0x0C
// // #define BitFramingReg 0x0D
// // #define ModeReg 0x11
// // #define TxControlReg 0x14
// // #define TxASKReg 0x15
// // #define CRCResultRegH 0x21
// // #define CRCResultRegL 0x22
// // #define TModeReg 0x2A
// // #define TPrescalerReg 0x2B
// // #define TReloadRegH 0x2C
// // #define TReloadRegL 0x2D
// // #define VersionReg 0x37

// // typedef struct {
// //     int spi_channel;
// //     int spi_handle;
// //     int rst_pin;
// //     int ss_pin;
// // } MFRC522;

// // // Prototipos de funciones
// // void MFRC522_Init(MFRC522 *dev, int rst_pin, int ss_pin);
// // void MFRC522_Reset(MFRC522 *dev);
// // uint8_t MFRC522_Request(MFRC522 *dev, uint8_t reqMode, uint8_t *TagType);
// // uint8_t MFRC522_Anticoll(MFRC522 *dev, uint8_t *serNum);
// // uint8_t MFRC522_Auth(MFRC522 *dev, uint8_t authMode, uint8_t blockAddr, uint8_t *key, uint8_t *uid);
// // uint8_t MFRC522_Read(MFRC522 *dev, uint8_t blockAddr, uint8_t *recvData);
// // uint8_t MFRC522_Write(MFRC522 *dev, uint8_t blockAddr, uint8_t *data);
// // void MFRC522_Halt(MFRC522 *dev);
// // void MFRC522_StopCrypto1(MFRC522 *dev);
// // void MFRC522_CalculateCRC(MFRC522 *dev, uint8_t *data, uint8_t len, uint8_t *result);
// // uint8_t MFRC522_ToCard(MFRC522 *dev, uint8_t command, uint8_t *sendData, uint8_t sendLen,
// //                       uint8_t *backData, uint8_t *backLen);
// // uint8_t Read_MFRC522(MFRC522 *dev, uint8_t addr);
// // void Write_MFRC522(MFRC522 *dev, uint8_t addr, uint8_t val);
// // void SetBitMask(MFRC522 *dev, uint8_t reg, uint8_t mask);
// // void ClearBitMask(MFRC522 *dev, uint8_t reg, uint8_t mask);

// // #endif

// // // #ifndef MFRC522_H
// // // #define MFRC522_H

// // // #include <stdint.h>

// // // #define MAX_LEN 16
// // // #define MI_OK 0
// // // #define MI_NOTAGERR 1
// // // #define MI_ERR 2

// // // #define PCD_IDLE 0x00
// // // #define PCD_AUTHENT 0x0E
// // // #define PCD_RECEIVE 0x08
// // // #define PCD_TRANSMIT 0x04
// // // #define PCD_TRANSCEIVE 0x0C
// // // #define PCD_RESETPHASE 0x0F
// // // #define PCD_CALCCRC 0x03

// // // #define PICC_REQIDL 0x26
// // // #define PICC_ANTICOLL 0x93
// // // #define PICC_AUTHENT1A 0x60
// // // #define PICC_READ 0x30
// // // #define PICC_WRITE 0xA0
// // // #define PICC_HALT 0x50

// // // #define CommandReg 0x01
// // // #define CommIEnReg 0x02
// // // #define CommIrqReg 0x04
// // // #define DivIrqReg 0x05
// // // #define ErrorReg 0x06
// // // #define Status2Reg 0x08
// // // #define FIFODataReg 0x09
// // // #define FIFOLevelReg 0x0A
// // // #define ControlReg 0x0C
// // // #define BitFramingReg 0x0D
// // // #define ModeReg 0x11
// // // #define TxControlReg 0x14
// // // #define TxASKReg 0x15
// // // #define CRCResultRegH 0x21
// // // #define CRCResultRegL 0x22
// // // #define TModeReg 0x2A
// // // #define TPrescalerReg 0x2B
// // // #define TReloadRegH 0x2C
// // // #define TReloadRegL 0x2D

// // // typedef struct
// // // {
// // //     int spi_channel;
// // //     int rst_pin;
// // //     int ss_pin;
// // //     int spi_handle;
// // // } MFRC522;

// // // void MFRC522_Init(MFRC522 *dev, int rst_pin, int ss_pin);
// // // void MFRC522_Reset(MFRC522 *dev);
// // // uint8_t MFRC522_Request(MFRC522 *dev, uint8_t reqMode, uint8_t *TagType);
// // // uint8_t MFRC522_Anticoll(MFRC522 *dev, uint8_t *serNum);
// // // uint8_t MFRC522_Read(MFRC522 *dev, uint8_t blockAddr, uint8_t *recvData);
// // // void MFRC522_Halt(MFRC522 *dev);
// // // uint8_t MFRC522_Auth(MFRC522 *dev, uint8_t authMode, uint8_t blockAddr, uint8_t *key, uint8_t *uid);
// // // void MFRC522_StopCrypto1(MFRC522 *dev);
// // // void MFRC522_CalculateCRC(MFRC522 *dev, uint8_t *data, uint8_t len, uint8_t *result);
// // // uint8_t MFRC522_ToCard(MFRC522 *dev, uint8_t command, uint8_t *sendData, uint8_t sendLen,
// // //                        uint8_t *backData, uint8_t *backLen);
// // // uint8_t Read_MFRC522(MFRC522 *dev, uint8_t addr);

// // // void SetBitMask(MFRC522 *dev, uint8_t reg, uint8_t mask);
// // // void ClearBitMask(MFRC522 *dev, uint8_t reg, uint8_t mask);


// // // #endif
