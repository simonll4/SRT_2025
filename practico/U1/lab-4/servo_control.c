#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <pigpio.h>
#include <unistd.h>
#include <signal.h>
#include <stdbool.h>

// Configuraciones
#define SERVO_PIN 18
#define MPU6050_ADDR 0x68
#define ACCEL_XOUT_H 0x3B
#define ACCEL_ZOUT_H 0x3F
#define UPDATE_DELAY 10000 // 10ms

// PWM
#define MIN_PULSE 500
#define MAX_PULSE 2500
#define MIN_ANGLE 0
#define MAX_ANGLE 180

// Variables globales
int i2c_handle;
volatile bool keep_running = true;

// Manejo de Ctrl+C
void handle_sigint(int sig)
{
    keep_running = false;
}

// Inicializa el MPU6050
void mpu6050_init()
{
    i2cWriteByteData(i2c_handle, 0x6B, 0x00); // Quita sleep mode
}

// Lee dos registros del MPU6050 y retorna valor con signo
short read_accel(int reg)
{
    int high = i2cReadByteData(i2c_handle, reg);
    int low = i2cReadByteData(i2c_handle, reg + 1);

    if (high < 0 || low < 0)
    {
        fprintf(stderr, "Error al leer acelerómetro (reg 0x%X)\n", reg);
        return 0;
    }

    return (int16_t)((high << 8) | low);
}

// Convierte un ángulo (0°–180°) a pulso PWM (500–2500 μs)
int angle_to_pulse(float angle)
{
    if (angle < MIN_ANGLE)
        angle = MIN_ANGLE;
    if (angle > MAX_ANGLE)
        angle = MAX_ANGLE;
    float scale = (MAX_PULSE - MIN_PULSE) / (float)(MAX_ANGLE - MIN_ANGLE);
    return MIN_PULSE + (int)(angle * scale);
}

// Suaviza los cambios con media exponencial
float suavizar(float anterior, float nuevo, float factor)
{
    return anterior * (1.0 - factor) + nuevo * factor;
}

int main()
{
    signal(SIGINT, handle_sigint); // Ctrl+C handler

    // Inicializar pigpio
    if (gpioInitialise() < 0)
    {
        fprintf(stderr, "Error al inicializar pigpio\n");
        return 1;
    }

    // Inicializar I2C
    i2c_handle = i2cOpen(1, MPU6050_ADDR, 0);
    if (i2c_handle < 0)
    {
        fprintf(stderr, "Error al abrir I2C\n");
        gpioTerminate();
        return 1;
    }

    mpu6050_init();

    printf("Control de Servo SG90 con MPU6050 (Ctrl+C para salir)\n\n");

    float servo_angle = 90.0; // Arranca en el medio

    while (keep_running)
    {
        // Leer aceleraciones
        short accel_x = read_accel(ACCEL_XOUT_H);
        short accel_z = read_accel(ACCEL_ZOUT_H);

        float accel_x_g = accel_x / 16384.0;
        float accel_z_g = accel_z / 16384.0;

        // Ángulo en radianes → grados
        float angle_rad = atan2(accel_x_g, accel_z_g);
        float angle_deg = angle_rad * 180.0 / M_PI;

        // Escalar de [-90, 90] a [0, 180]
        float raw_angle = angle_deg + 90.0;

        // Suavizar
        servo_angle = suavizar(servo_angle, raw_angle, 0.1);

        // Convertir a PWM
        int pulse_width = angle_to_pulse(servo_angle);

        // Enviar al servo
        gpioServo(SERVO_PIN, pulse_width);

        // Mostrar info
        printf("Ángulo: %.2f° | Pulso: %d μs | X: %.2fg | Z: %.2fg\n",
               servo_angle, pulse_width, accel_x_g, accel_z_g);

        usleep(UPDATE_DELAY);
    }

    // Detener servo y limpiar
    gpioServo(SERVO_PIN, 0); // Desactiva PWM
    i2cClose(i2c_handle);
    gpioTerminate();

    printf("\nPrograma finalizado correctamente.\n");
    return 0;
}
