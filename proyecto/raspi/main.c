
// TODO: para cuando este listo gpio_feedback.c
// #include <stdio.h>
// #include <stdlib.h>
// #include <unistd.h>
// #include <sys/wait.h>
// #include <semaphore.h>
// #include <fcntl.h>
// #include <string.h>
// #include <signal.h>
// #include "gpio_feedback.h"

// #define SEM_NAME "/rfid_sem"
// #define SHM_NAME "/rfid_shm"
// #define SHM_SIZE 128

// int main()
// {
//     sem_t *sem = sem_open(SEM_NAME, O_CREAT, 0666, 1);
//     if (sem == SEM_FAILED)
//     {
//         perror("sem_open");
//         exit(1);
//     }

//     int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
//     ftruncate(shm_fd, SHM_SIZE * 2);

//     pid_t pid1 = fork();
//     if (pid1 == 0)
//     {
//         setenv("VIRTUAL_ENV", "/home/pipo/raspi/gui/.venv", 1);
//         setenv("PYTHONPATH", "/home/pipo/raspi", 1);
//         char new_path[1024];
//         snprintf(new_path, sizeof(new_path), "/home/pipo/raspi/gui/.venv/bin:%s", getenv("PATH"));
//         setenv("PATH", new_path, 1);
//         execl("/home/pipo/raspi/gui/.venv/bin/python", "python", "-m", "gui.services.rfid_reader", NULL);
//         perror("rfid_reader failed");
//         exit(1);
//     }

//     pid_t pid2 = fork();
//     if (pid2 == 0)
//     {
//         setenv("VIRTUAL_ENV", "/home/pipo/raspi/gui/.venv", 1);
//         setenv("PYTHONPATH", "/home/pipo/raspi", 1);
//         char new_path[1024];
//         snprintf(new_path, sizeof(new_path), "/home/pipo/raspi/gui/.venv/bin:%s", getenv("PATH"));
//         setenv("PATH", new_path, 1);
//         execl("/home/pipo/raspi/gui/.venv/bin/python", "python", "-m", "gui.gui", NULL);
//         perror("gui failed");
//         exit(1);
//     }

//     pid_t pid3 = fork();
//     if (pid3 == 0)
//     {
//         run_gpio_feedback(); // Ya está importado
//     }

//     int status;
//     pid_t exited_pid = wait(&status);
//     printf("Proceso %d terminó. Matando a los demás...\n", exited_pid);

//     kill(pid1, SIGTERM);
//     kill(pid2, SIGTERM);
//     kill(pid3, SIGTERM);

//     wait(NULL);
//     wait(NULL);

//     sem_unlink(SEM_NAME);
//     shm_unlink(SHM_NAME);
//     unlink("/tmp/gpio_feedback.sock");

//     return 0;
// }

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <string.h>

#include <semaphore.h>
#define SEM_NAME "/rfid_sem"

#define SHM_NAME "/rfid_shm"
#define SHM_SIZE 128

int main()
{
    // Crear semáforo
    sem_t *sem = sem_open(SEM_NAME, O_CREAT, 0666, 1);
    if (sem == SEM_FAILED)
    {
        perror("sem_open");
        exit(1);
    }

    // Crear memoria compartida
    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    // ftruncate(shm_fd, SHM_SIZE);
    ftruncate(shm_fd, SHM_SIZE * 2);

    pid_t pid1 = fork();
    if (pid1 == 0)
    {
        // Configurar entorno para el venv
        setenv("VIRTUAL_ENV", "/home/pipo/raspi/gui/.venv", 1);
        setenv("PYTHONPATH", "/home/pipo/raspi", 1);

        // Construir el nuevo PATH
        char new_path[1024];
        snprintf(new_path, sizeof(new_path),
                 "/home/pipo/raspi/gui/.venv/bin:%s",
                 getenv("PATH"));
        setenv("PATH", new_path, 1);

        // Ejecutar el script
        execl("/home/pipo/raspi/gui/.venv/bin/python",
              "python", "-m", "gui.services.rfid_reader",
              NULL);
        perror("Error al ejecutar rfid_reader.py");
        exit(1);
    }

    pid_t pid2 = fork();
    if (pid2 == 0)
    {
        // Mismo setup para el segundo script
        setenv("VIRTUAL_ENV", "/home/pipo/raspi/gui/.venv", 1);
        setenv("PYTHONPATH", "/home/pipo/raspi", 1);

        char new_path[1024];
        snprintf(new_path, sizeof(new_path),
                 "/home/pipo/raspi/gui/.venv/bin:%s",
                 getenv("PATH"));
        setenv("PATH", new_path, 1);

        execl("/home/pipo/raspi/gui/.venv/bin/python",
              "python", "-m", "gui.gui", // ¡Cambiado!
              NULL);
        perror("Error al ejecutar gui.py");
        exit(1);
    }

    // Esperar hijos
    wait(NULL);
    wait(NULL);

    // Limpiar semáforo
    sem_unlink(SEM_NAME);

    // Limpiar memoria compartida
    shm_unlink(SHM_NAME);

    return 0;
}
