#ifndef RC522_H
#define RC522_H

#include <stdint.h>
#include <unistd.h>

// Estados
#define MI_OK       0
#define MI_ERR      1

// Comandos
#define PCD_IDLE        0x00
#define PCD_TRANSCEIVE  0x0C
#define PCD_RESETPHASE  0x0F

// Registros
#define CommandReg      0x01
#define CommIEnReg      0x02
#define CommIrqReg      0x04
#define DivIEnReg       0x05
#define ErrorReg        0x06
#define Status1Reg      0x07
#define Status2Reg      0x08
#define FIFODataReg     0x09
#define FIFOLevelReg    0x0A
#define WaterLevelReg   0x0B
#define ControlReg      0x0C
#define BitFramingReg   0x0D
#define CollReg         0x0E
#define ModeReg         0x11
#define TxControlReg    0x14
#define TxASKReg        0x15
#define TMReloadRegH    0x2C
#define TMReloadRegL    0x2D
#define RFCfgReg        0x26
#define TModeReg        0x2A
#define TPrescalerReg   0x2B
#define TReloadRegH     0x2C
#define TReloadRegL     0x2D
#define PICC_REQALL 0x52
#define PCD_TRANSCEIVE  0x0C 

// Funciones públicas
void rc522_init(int handle);
int rc522_check_card(uint8_t *uid);
int rc522_to_card(uint8_t command, uint8_t *send_data, int send_len, uint8_t *back_data);
uint8_t rc522_get_version();
uint8_t read_register(uint8_t reg);
void write_register(uint8_t reg, uint8_t val);

#endif