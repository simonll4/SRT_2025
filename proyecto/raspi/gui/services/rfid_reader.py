import mmap
import time
import os
import RPi.GPIO as GPIO
import posix_ipc
from mfrc522 import SimpleMFRC522

from gui.constants import SHM_NAME, SHM_SIZE, SEM_NAME


def main():
    reader = SimpleMFRC522()
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    try:
        # Configurar semáforo y memoria compartida
        sem = posix_ipc.Semaphore(SEM_NAME)
        fd = os.open(f"/dev/shm{SHM_NAME}", os.O_CREAT | os.O_RDWR, 0o666)
        os.ftruncate(fd, SHM_SIZE * 2)
        shm = mmap.mmap(fd, SHM_SIZE * 2, mmap.MAP_SHARED, mmap.PROT_WRITE)

        while True:
            try:
                print("Esperando producto RFID...")
                id, text = reader.read()
                text = text.strip() if text else ""

                print(f"Producto leído: ID={id}, Nombre={text}")

                sem.acquire()  # Bloqueo para escritura

                shm.seek(0)
                shm.write(f"{id}".encode("utf-8").ljust(SHM_SIZE, b"\x00"))
                shm.seek(SHM_SIZE)
                shm.write(text.encode("utf-8").ljust(SHM_SIZE, b"\x00"))

                sem.release()  # Liberar semáforo

                time.sleep(2)
            except Exception as e:
                print(f"Error leyendo producto: {e}")
                time.sleep(1)

    finally:
        GPIO.cleanup()
        if "shm" in locals():
            shm.close()
        if fd:
            os.close(fd)


if __name__ == "__main__":
    main()
