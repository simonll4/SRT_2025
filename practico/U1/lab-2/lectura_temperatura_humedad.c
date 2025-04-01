#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <pigpio.h>

// Dirección I2C del sensor AHT10
#define AHT10_ADDRESS 0x38

// Comandos del sensor AHT10
#define AHT10_INIT_CMD 0xE1
#define AHT10_TRIGGER_MEASUREMENT_CMD 0xAC
#define AHT10_SOFT_RESET_CMD 0xBA

// Pines GPIO para las salidas
#define TEMP_OUTPUT_GPIO 17     // GPIO para temperatura > 25°C
#define HUMIDITY_OUTPUT_GPIO 27 // GPIO para humedad > 70%

// Handle para la comunicación I2C
int i2c_handle;
volatile sig_atomic_t stop = 0;

// Manejador de señal para salida segura
void handle_signal(int signum)
{
    stop = 1;
}

// Función para inicializar el sensor AHT10AHT10_ADDRESS
int initialize_aht10()
{
    char init_cmd[3] = {AHT10_INIT_CMD, 0x08, 0x00};

    // Enviar comando de inicialización
    if (i2cWriteDevice(i2c_handle, init_cmd, 3) != 0)
    {
        fprintf(stderr, "Error al inicializar el sensor AHT10\n");
        return -1;
    }
    usleep(10000);

    // Verificar si el sensor responde correctamente
    char status;
    if (i2cReadDevice(i2c_handle, &status, 1) != 1 || (status & 0x18) != 0x18)
    {
        fprintf(stderr, "Error: Sensor no inicializado correctamente\n");
        return -1;
    }
    return 0;
}

// Función para realizar un soft reset del sensor
void soft_reset_aht10()
{
    char reset_cmd = AHT10_SOFT_RESET_CMD;
    i2cWriteDevice(i2c_handle, &reset_cmd, 1);
    usleep(20000);
}

// Función para leer temperatura y humedad
int read_aht10(float *temperature, float *humidity)
{
    char trigger_cmd[3] = {AHT10_TRIGGER_MEASUREMENT_CMD, 0x33, 0x00};
    char data[6] = {0};

    // hasta 3 intentos antes de resetear el sensor
    for (int attempt = 0; attempt < 3; attempt++)
    {
        if (i2cWriteDevice(i2c_handle, trigger_cmd, 3) != 0)
        {
            fprintf(stderr, "Error al enviar comando de medición\n");
            continue;
        }
        usleep(80000);
        if (i2cReadDevice(i2c_handle, data, 6) == 6 && (data[0] & 0x80) == 0)
        {
            uint32_t humid_data = ((uint32_t)data[1] << 12) | ((uint32_t)data[2] << 4) | (data[3] >> 4);
            *humidity = (float)humid_data / (1 << 20) * 100.0;
            uint32_t temp_data = ((uint32_t)(data[3] & 0x0F) << 16) | ((uint32_t)data[4] << 8) | data[5];
            *temperature = (float)temp_data / (1 << 20) * 200.0 - 50.0;
            return 0;
        }
    }
    return -1;
}

// Función para controlar las salidas GPIO según los umbrales
void control_outputs(float temperature, float humidity)
{
    gpioWrite(TEMP_OUTPUT_GPIO, temperature > 25.0 ? 1 : 0);
    gpioWrite(HUMIDITY_OUTPUT_GPIO, humidity > 70.0 ? 1 : 0);
}

int main()
{
    signal(SIGINT, handle_signal);

    if (gpioInitialise() < 0)
    {
        fprintf(stderr, "Error al inicializar pigpio\n");
        return 1;
    }

    i2c_handle = i2cOpen(1, AHT10_ADDRESS, 0);
    if (i2c_handle < 0)
    {
        fprintf(stderr, "Error al abrir comunicación I2C\n");
        gpioTerminate();
        return 1;
    }

    gpioSetMode(TEMP_OUTPUT_GPIO, PI_OUTPUT);
    gpioSetMode(HUMIDITY_OUTPUT_GPIO, PI_OUTPUT);

    if (initialize_aht10() != 0)
    {
        fprintf(stderr, "Fallo en la inicialización del sensor\n");
        i2cClose(i2c_handle);
        gpioTerminate();
        return 1;
    }

    printf("Sensor AHT10 inicializado correctamente\n");

    while (!stop)
    {
        float temperature = 0.0;
        float humidity = 0.0;

        if (read_aht10(&temperature, &humidity) == 0)
        {
            printf("Temperatura: %.2f °C, Humedad: %.2f %%\n", temperature, humidity);
            control_outputs(temperature, humidity);
        }
        else
        {
            fprintf(stderr, "Error al leer del sensor, intentando reset...\n");
            soft_reset_aht10();
            initialize_aht10();
        }

        sleep(1);
    }

    gpioWrite(TEMP_OUTPUT_GPIO, 0);
    gpioWrite(HUMIDITY_OUTPUT_GPIO, 0);
    i2cClose(i2c_handle);
    gpioTerminate();
    printf("Programa terminado correctamente\n");
    return 0;
}


 