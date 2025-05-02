#include <stdio.h>
#include <string.h>
#include <pigpio.h>
#include "rc522.h"

static int spi_handle;
#define MAX_LEN 16

uint8_t read_register(uint8_t reg)
{
    char buf[2];
    buf[0] = ((reg << 1) & 0x7E) | 0x80;
    buf[1] = 0;
    spiXfer(spi_handle, buf, buf, 2);
    return buf[1];
}

void write_register(uint8_t reg, uint8_t val)
{
    char buf[2];
    buf[0] = (reg << 1) & 0x7E;
    buf[1] = val;
    spiWrite(spi_handle, buf, 2);
}

static void set_bit_mask(uint8_t reg, uint8_t mask)
{
    uint8_t tmp = read_register(reg);
    write_register(reg, tmp | mask);
}

static void clear_bit_mask(uint8_t reg, uint8_t mask)
{
    uint8_t tmp = read_register(reg);
    write_register(reg, tmp & (~mask));
}

void rc522_init(int handle) {
    spi_handle = handle;
    
    // Reset hardware
    gpioSetMode(25, PI_OUTPUT);
    gpioWrite(25, 0);
    usleep(100000);  // 100ms reset
    gpioWrite(25, 1);
    usleep(50000);
    
    // Configuración mejorada
    write_register(CommandReg, PCD_RESETPHASE);
    usleep(2000);
    
    write_register(TModeReg, 0x8D);
    write_register(TPrescalerReg, 0x3E);
    write_register(TReloadRegL, 0x30);
    write_register(TReloadRegH, 0xE8);
    
    write_register(TxASKReg, 0x40);
    write_register(ModeReg, 0x3D);
    
    // Activa antena
    write_register(TxControlReg, 0x83);
    usleep(1000);
}

uint8_t rc522_get_version()
{
    return read_register(0x37); // VersionReg
}

int rc522_to_card(uint8_t command, uint8_t *send_data, int send_len, uint8_t *back_data)
{
    uint8_t irq_en = 0x00;
    uint8_t wait_irq = 0x00;
    uint8_t status = MI_ERR;
    uint8_t last_bits;
    uint8_t n;
    int i;
    uint8_t back_len = 0;

    if (command == PCD_TRANSCEIVE)
    {
        irq_en = 0x77;
        wait_irq = 0x30;
    }

    write_register(CommIEnReg, irq_en | 0x80);
    clear_bit_mask(CommIrqReg, 0x80);
    set_bit_mask(FIFOLevelReg, 0x80);

    write_register(CommandReg, PCD_IDLE);

    for (i = 0; i < send_len; i++)
    {
        write_register(FIFODataReg, send_data[i]);
    }

    write_register(CommandReg, command);

    if (command == PCD_TRANSCEIVE)
    {
        set_bit_mask(BitFramingReg, 0x80);
    }

    i = 4000;
    do
    {
        n = read_register(CommIrqReg);
        i--;
    } while (i && !(n & 0x01) && !(n & wait_irq));

    clear_bit_mask(BitFramingReg, 0x80);

    if (i)
    {
        if (!(read_register(ErrorReg) & 0x1B))
        {
            status = MI_OK;
            if (command == PCD_TRANSCEIVE)
            {
                n = read_register(FIFOLevelReg);
                last_bits = read_register(ControlReg) & 0x07;
                if (last_bits)
                {
                    back_len = (n - 1) * 8 + last_bits;
                }
                else
                {
                    back_len = n * 8;
                }

                for (i = 0; i < n; i++)
                {
                    back_data[i] = read_register(FIFODataReg);
                }
            }
        }
    }

    return status;
}

int rc522_check_card(uint8_t *uid) {
    uint8_t back_data[MAX_LEN];
    uint8_t req_code = 0x26;  // PICC_REQIDL
    
    // 1. Clear FIFO
    write_register(CommandReg, PCD_IDLE);
    write_register(FIFOLevelReg, 0x80); // Clear FIFO buffer
    
    // 2. Send request command
    if (rc522_to_card(PCD_TRANSCEIVE, &req_code, 1, back_data) != MI_OK) {
        return MI_ERR;
    }
    
    // 3. Anti-collision
    uint8_t anti_coll[] = {0x93, 0x20};
    if (rc522_to_card(PCD_TRANSCEIVE, anti_coll, 2, back_data) != MI_OK) {
        return MI_ERR;
    }
    
    // 4. Validate UID (4-7 bytes)
    if (back_data[0] != 0x00) {
        memcpy(uid, back_data, 4); // Standard 4-byte UID
        return MI_OK;
    }
    
    return MI_ERR;
}