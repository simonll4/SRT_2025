all: productor consumidor

productor: productor.c buffer.c
	gcc -o productor productor.c buffer.c -lrt -pthread

consumidor: consumidor.c buffer.c
	gcc -o consumidor consumidor.c buffer.c -lrt -pthread

clean:
	rm -f productor consumidor
