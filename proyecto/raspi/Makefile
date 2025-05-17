CC = gcc
CFLAGS = -Wall -Wextra -g
LDFLAGS = -lpigpio -lrt -pthread

all: main

main: main.c gpio_feedback.c gpio_feedback.h
	$(CC) $(CFLAGS) main.c gpio_feedback.c -o main $(LDFLAGS)

clean:
	rm -f main
