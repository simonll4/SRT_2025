#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <string.h>

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
        // execl("/home/pipo/raspi/gui/.venv/bin/python",
        //       "python",
        //       "/home/pipo/raspi/gui/services/rfid_reader.py",
        //       NULL);
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

        // execl("/home/pipo/raspi/gui/.venv/bin/python",
        //       "python",
        //       "/home/pipo/raspi/gui/gui.py",
        //       NULL);
        execl("/home/pipo/raspi/gui/.venv/bin/python",
              "python", "-m", "gui.gui", // ¡Cambiado!
              NULL);
        perror("Error al ejecutar gui.py");
        exit(1);
    }

    // Esperar hijos
    wait(NULL);
    wait(NULL);

    // Limpiar memoria compartida
    shm_unlink(SHM_NAME);

    return 0;
}
