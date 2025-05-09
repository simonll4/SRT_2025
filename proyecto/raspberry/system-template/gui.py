# gui.py
import tkinter as tk
import mmap
import os
import time
import threading

SHM_NAME = "/rfid_shm"
SHM_SIZE = 128


class RFIDGui:
    def __init__(self, root):
        self.root = root
        self.label = tk.Label(root, text="Esperando UID...", font=("Arial", 24))
        self.label.pack(padx=20, pady=40)

        fd = os.open(f"/dev/shm{SHM_NAME}", os.O_RDONLY)
        self.shm = mmap.mmap(fd, SHM_SIZE, access=mmap.ACCESS_READ)

        self.update_label()

    def update_label(self):
        self.shm.seek(0)
        data = self.shm.read(SHM_SIZE).rstrip(b"\x00").decode("utf-8")
        self.label.config(text=f"UID: {data}")
        self.root.after(1000, self.update_label)


def main():
    root = tk.Tk()
    root.title("RFID Reader GUI")
    gui = RFIDGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
