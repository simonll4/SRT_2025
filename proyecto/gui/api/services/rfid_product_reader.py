import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time

class RFIDProductReader:
    def __init__(self):
        self.reader = SimpleMFRC522()
        self.last_id = None

    def read_product(self):
        """Lee una tarjeta RFID de producto y espera que se retire antes de permitir otra lectura."""
        try:
            print("Esperando producto RFID...")
            while True:
                id, text = self.reader.read()
                if str(id) != self.last_id:
                    print(f"Producto leído: ID={id}, Nombre={text.strip()}")
                    self.last_id = str(id)
                    # Espera a que el tag sea retirado
                    time.sleep(1.5)
                    return {"id": str(id), "name": text.strip()}
                time.sleep(0.5)  # Espera antes de volver a intentar
        except Exception as e:
            print(f"Error leyendo producto: {e}")
            raise
        finally:
            GPIO.cleanup()
