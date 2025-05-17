#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <pigpio.h>

#define SOCKET_PATH "/tmp/gpio_feedback.sock"
#define LED_GREEN 17
#define LED_RED 27
#define BUZZER 22

// TODO: revisar antes de probar

void run_gpio_feedback()
{
    if (gpioInitialise() < 0)
    {
        fprintf(stderr, "pigpio init failed\n");
        exit(1);
    }

    gpioSetMode(LED_GREEN, PI_OUTPUT);
    gpioSetMode(LED_RED, PI_OUTPUT);
    gpioSetMode(BUZZER, PI_OUTPUT);

    int server_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (server_fd < 0)
    {
        perror("socket");
        exit(1);
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path) - 1);
    unlink(SOCKET_PATH);

    if (bind(server_fd, (struct sockaddr *)&addr, sizeof(addr)) == -1)
    {
        perror("bind");
        exit(1);
    }

    if (listen(server_fd, 5) == -1)
    {
        perror("listen");
        exit(1);
    }

    while (1)
    {
        int client_fd = accept(server_fd, NULL, NULL);
        if (client_fd == -1)
        {
            perror("accept");
            continue;
        }

        char buffer[64] = {0};
        read(client_fd, buffer, sizeof(buffer));
        close(client_fd);

        if (strcmp(buffer, "SUCCESS") == 0)
        {
            gpioWrite(LED_RED, 0);
            gpioWrite(LED_GREEN, 1);
            gpioWrite(BUZZER, 1);
            usleep(200000);
            gpioWrite(BUZZER, 0);
            gpioWrite(LED_GREEN, 0);
        }
        else if (strcmp(buffer, "FAILURE") == 0)
        {
            gpioWrite(LED_GREEN, 0);
            gpioWrite(LED_RED, 1);
            gpioWrite(BUZZER, 1);
            usleep(500000);
            gpioWrite(BUZZER, 0);
            gpioWrite(LED_RED, 0);
        }
    }

    close(server_fd);
    unlink(SOCKET_PATH);
    gpioTerminate();
    exit(0);
}
