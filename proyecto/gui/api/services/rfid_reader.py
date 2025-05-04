import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time

class RFIDReader:
    def __init__(self):
        self.reader = SimpleMFRC522()
        
    def read_card(self):
        """Lee una tarjeta RFID y devuelve el ID."""
        try:
            print("Esperando tarjeta RFID...")
            id, _ = self.reader.read()
            print(f"ID de tarjeta leída: {id}")
            return str(id)
        except Exception as e:
            print(f"Error leyendo tarjeta: {e}")
            raise
        finally:
            GPIO.cleanup()