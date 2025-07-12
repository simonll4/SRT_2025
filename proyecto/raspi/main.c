
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
#include <semaphore.h>
#include <fcntl.h>
#include <string.h>
#include <signal.h>
#include "gpio_feedback.h"

#define SEM_NAME "/rfid_sem"
#define SHM_NAME "/rfid_shm"
#define SHM_SIZE 128

int main()
{
    sem_t *sem = sem_open(SEM_NAME, O_CREAT, 0666, 1);
    if (sem == SEM_FAILED)
    {
        perror("sem_open");
        exit(1);
    }

    int shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    ftruncate(shm_fd, SHM_SIZE * 2);

    pid_t pid1 = fork();
    if (pid1 == 0)
    {
        // Configurar variables de entorno para X11
        setenv("DISPLAY", ":0", 1);
        setenv("XAUTHORITY", "/home/pipo/.Xauthority", 1);
        
        setenv("VIRTUAL_ENV", "/home/pipo/raspi/gui/.venv", 1);
        setenv("PYTHONPATH", "/home/pipo/raspi", 1);
        char new_path[1024];
        snprintf(new_path, sizeof(new_path), "/home/pipo/raspi/gui/.venv/bin:%s", getenv("PATH"));
        setenv("PATH", new_path, 1);
        execl("/home/pipo/raspi/gui/.venv/bin/python", "python", "-m", "gui.services.rfid_reader", NULL);
        perror("rfid_reader failed");
        exit(1);
    }

    pid_t pid2 = fork();
    if (pid2 == 0)
    {
        // Configurar variables de entorno para X11
        setenv("DISPLAY", ":0", 1);
        setenv("XAUTHORITY", "/home/pipo/.Xauthority", 1);
        
        setenv("VIRTUAL_ENV", "/home/pipo/raspi/gui/.venv", 1);
        setenv("PYTHONPATH", "/home/pipo/raspi", 1);
        char new_path[1024];
        snprintf(new_path, sizeof(new_path), "/home/pipo/raspi/gui/.venv/bin:%s", getenv("PATH"));
        setenv("PATH", new_path, 1);
        execl("/home/pipo/raspi/gui/.venv/bin/python", "python", "-m", "gui.gui", NULL);
        perror("gui failed");
        exit(1);
    }

    pid_t pid3 = fork();
    if (pid3 == 0)
    {
        run_gpio_feedback();
    }

    int status;
    pid_t exited_pid = wait(&status);
    printf("Proceso %d terminó. Matando a los demás...\n", exited_pid);

    kill(pid1, SIGTERM);
    kill(pid2, SIGTERM);
    kill(pid3, SIGTERM);

    wait(NULL);
    wait(NULL);

    sem_unlink(SEM_NAME);
    shm_unlink(SHM_NAME);
    unlink("/tmp/gpio_feedback.sock");

    return 0;
}

