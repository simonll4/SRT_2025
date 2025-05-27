#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>

#define SOCKET_PATH "/tmp/led_control.sock"
#define BUFFER_SIZE 1024

int main() {
    int server_fd, client_fd;
    struct sockaddr_un server_addr, client_addr;
    char buffer[BUFFER_SIZE];
    int led_state = 0; // 0 = apagado, 1 = encendido

    // Crear socket
    server_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (server_fd == -1) {
        perror("Error al crear el socket");
        exit(EXIT_FAILURE);
    }

    // Configurar dirección del servidor
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sun_family = AF_UNIX;
    strncpy(server_addr.sun_path, SOCKET_PATH, sizeof(server_addr.sun_path) - 1);

    // Eliminar el socket si ya existe
    unlink(SOCKET_PATH);

    // Vincular socket a la dirección
    if (bind(server_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("Error al vincular el socket");
        exit(EXIT_FAILURE);
    }

    // Escuchar conexiones
    if (listen(server_fd, 5) == -1) {
        perror("Error al escuchar");
        exit(EXIT_FAILURE);
    }

    printf("Servidor iniciado. Esperando conexiones...\n");

    while (1) {
        socklen_t client_len = sizeof(client_addr);
        client_fd = accept(server_fd, (struct sockaddr*)&client_addr, &client_len);
        if (client_fd == -1) {
            perror("Error al aceptar la conexión");
            continue;
        }

        printf("Nuevo cliente conectado\n");

        // Mantener la conexión abierta hasta que el cliente se desconecte
        while (1) {
            // Recibir comando del cliente
            ssize_t bytes_received = recv(client_fd, buffer, BUFFER_SIZE - 1, 0);
            if (bytes_received <= 0) {
                printf("Cliente desconectado\n");
                break;
            }

            buffer[bytes_received] = '\0';
            printf("Comando recibido: %s\n", buffer);

            // Procesar comando
            if (strcmp(buffer, "ON") == 0) {
                if (led_state == 1) {
                    strcpy(buffer, "El LED ya está encendido");
                } else {
                    led_state = 1;
                    strcpy(buffer, "LED encendido");
                }
            } else if (strcmp(buffer, "OFF") == 0) {
                if (led_state == 0) {
                    strcpy(buffer, "El LED ya está apagado");
                } else {
                    led_state = 0;
                    strcpy(buffer, "LED apagado");
                }
            } else if (strcmp(buffer, "STATUS") == 0) {
                sprintf(buffer, "Estado del LED: %s", led_state ? "ENCENDIDO" : "APAGADO");
            } else {
                strcpy(buffer, "Comando no válido");
            }

            // Enviar respuesta al cliente
            if (send(client_fd, buffer, strlen(buffer), 0) == -1) {
                perror("Error al enviar respuesta");
                break;
            }
        }

        close(client_fd);
    }

    close(server_fd);
    unlink(SOCKET_PATH);
    return 0;
} 