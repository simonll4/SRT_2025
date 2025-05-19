#ifndef BUFFER_H
#define BUFFER_H

#include <semaphore.h>
#include <fcntl.h>

#define BUFFER_SIZE 10
#define SHM_NAME "/shared_buffer"

typedef struct {
    int data[BUFFER_SIZE];
    int in;
    int out;
    sem_t empty;
    sem_t full;
    sem_t mutex;
} SharedBuffer;

SharedBuffer* init_shared_buffer(int create);

#endif
