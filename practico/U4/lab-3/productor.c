#include "buffer.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include "buffer.h"


int main() {
    SharedBuffer* buffer = init_shared_buffer(1); // Crea el buffer
    srand(time(NULL));

    while (1) {
        int item = rand() % 100;
        sem_wait(&buffer->empty);
        sem_wait(&buffer->mutex);

        buffer->data[buffer->in] = item;
        printf("Productor: produjo %d en %d\n", item, buffer->in);
        buffer->in = (buffer->in + 1) % BUFFER_SIZE;

        sem_post(&buffer->mutex);
        sem_post(&buffer->full);

        sleep(1); // producción lenta
    }

    return 0;
}
