# rfid_reader.py
import mmap
import time
import os

SHM_NAME = "/rfid_shm"
SHM_SIZE = 128


def main():
    fd = os.open(f"/dev/shm{SHM_NAME}", os.O_RDWR)
    shm = mmap.mmap(fd, SHM_SIZE)

    # Simulamos lectura de tags RFID cada 3 segundos
    tags = ["12345678", "87654321", "ABCDEF12"]
    idx = 0

    while True:
        tag = tags[idx % len(tags)]
        shm.seek(0)
        shm.write(tag.encode("utf-8").ljust(SHM_SIZE, b"\x00"))
        print(f"[RFID] Escribiendo UID: {tag}")
        idx += 1
        time.sleep(3)


if __name__ == "__main__":
    main()
