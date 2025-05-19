#include "buffer.h"
#include <sys/mman.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

SharedBuffer* init_shared_buffer(int create) {
    int flags = O_RDWR;
    if (create) flags |= O_CREAT;

    int shm_fd = shm_open(SHM_NAME, flags, 0666);
    if (shm_fd == -1) {
        perror("shm_open");
        return NULL;
    }

    if (create) ftruncate(shm_fd, sizeof(SharedBuffer));

    SharedBuffer* buffer = mmap(NULL, sizeof(SharedBuffer), PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (buffer == MAP_FAILED) {
        perror("mmap");
        return NULL;
    }

    if (create) {
        buffer->in = 0;
        buffer->out = 0;
        sem_init(&buffer->empty, 1, BUFFER_SIZE);
        sem_init(&buffer->full, 1, 0);
        sem_init(&buffer->mutex, 1, 1);
    }

    return buffer;
}
