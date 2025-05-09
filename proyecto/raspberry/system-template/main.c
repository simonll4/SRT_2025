// main.c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <sys/mman.h>

#define SHM_NAME "/rfid_shm"
#define SHM_SIZE 128

int main()
{

    // Crear memoria compartida
    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    ftruncate(shm_fd, SHM_SIZE);

    pid_t pid1 = fork();
    if (pid1 == 0)
    {
        // Proceso hijo 1: Lector RFID
        execlp("python3", "python3", "rfid_reader.py", NULL);
        perror("Error al ejecutar rfid_reader.py");
        exit(1);
    }

    pid_t pid2 = fork();
    if (pid2 == 0)
    {
        // Proceso hijo 2: GUI
        execlp("python3", "python3", "gui.py", NULL);
        perror("Error al ejecutar gui.py");
        exit(1);
    }

    // Padre espera a que terminen los hijos
    wait(NULL);
    wait(NULL);

    // Limpiar shm
    shm_unlink(SHM_NAME);

    return 0;
}
