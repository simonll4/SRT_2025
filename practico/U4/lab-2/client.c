#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>

#define SOCKET_PATH "/tmp/led_control.sock"
#define BUFFER_SIZE 1024

int main() {
    int client_fd;
    struct sockaddr_un server_addr;
    char buffer[BUFFER_SIZE];
    char command[BUFFER_SIZE];

    // Crear socket
    client_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (client_fd == -1) {
        perror("Error al crear el socket");
        exit(EXIT_FAILURE);
    }

    // Configurar dirección del servidor
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sun_family = AF_UNIX;
    strncpy(server_addr.sun_path, SOCKET_PATH, sizeof(server_addr.sun_path) - 1);

    // Conectar al servidor
    if (connect(client_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("Error al conectar con el servidor");
        exit(EXIT_FAILURE);
    }

    printf("Cliente conectado al servidor.\n");
    printf("Comandos disponibles:\n");
    printf("  ON     - Encender el LED\n");
    printf("  OFF    - Apagar el LED\n");
    printf("  STATUS - Consultar estado del LED\n");
    printf("  EXIT   - Salir\n");

    while (1) {
        printf("\nIngrese un comando: ");
        if (fgets(command, BUFFER_SIZE, stdin) == NULL) {
            printf("Error al leer el comando\n");
            break;
        }
        command[strcspn(command, "\n")] = 0; // Eliminar el salto de línea

        if (strcmp(command, "EXIT") == 0) {
            printf("Cerrando conexión...\n");
            break;
        }

        // Enviar comando al servidor
        if (send(client_fd, command, strlen(command), 0) == -1) {
            perror("Error al enviar el comando");
            break;
        }

        // Recibir respuesta del servidor
        ssize_t bytes_received = recv(client_fd, buffer, BUFFER_SIZE - 1, 0);
        if (bytes_received <= 0) {
            printf("Error: El servidor se ha desconectado\n");
            break;
        }
        buffer[bytes_received] = '\0';
        printf("Respuesta del servidor: %s\n", buffer);
    }

    close(client_fd);
    return 0;
} 