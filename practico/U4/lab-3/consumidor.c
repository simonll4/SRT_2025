#include "buffer.h"
#include <stdio.h>
#include <unistd.h>

int main()
{
    SharedBuffer *buffer = init_shared_buffer(0); // Solo lo abre

    while (1)
    {
        sem_wait(&buffer->full);
        sem_wait(&buffer->mutex);

        int item = buffer->data[buffer->out];
        printf("Consumidor: consumió %d en %d\n", item, buffer->out);
        buffer->out = (buffer->out + 1) % BUFFER_SIZE;

        sem_post(&buffer->mutex);
        sem_post(&buffer->empty);

        sleep(2); // procesamiento lento
    }

    return 0;
}
