import mmap
import time
import os
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

from gui.constants import SHM_NAME, SHM_SIZE


def main():
    reader = SimpleMFRC522()
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    try:
        # Configurar memoria compartida
        fd = os.open(f"/dev/shm{SHM_NAME}", os.O_CREAT | os.O_RDWR, 0o666)
        os.ftruncate(fd, SHM_SIZE * 2)  # Espacio para ID y texto
        shm = mmap.mmap(fd, SHM_SIZE * 2, mmap.MAP_SHARED, mmap.PROT_WRITE)

        GPIO.setwarnings(False)

        while True:
            try:
                print("Esperando producto RFID...")
                id, text = reader.read()
                text = text.strip() if text else ""

                print(f"Producto leído: ID={id}, Nombre={text}")

                # Convertir ID a string y escribir
                shm.seek(0)
                shm.write(f"{id}".encode("utf-8").ljust(SHM_SIZE, b"\x00"))
                # Escribir texto
                shm.seek(SHM_SIZE)
                shm.write(text.encode("utf-8").ljust(SHM_SIZE, b"\x00"))

                time.sleep(1.5)
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
