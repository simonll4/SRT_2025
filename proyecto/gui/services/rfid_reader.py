import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522


class RFIDReader:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RFIDReader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.reader = SimpleMFRC522()
        self.last_id = None
        self._initialized = True

    def read_product(self):
        GPIO.setwarnings(False)
        try:
            print("Esperando producto RFID...")
            id, text = self.reader.read()
            print(f"Producto leído: ID={id}, Nombre={text.strip()}")
            self.last_id = str(id)
            return {"id": str(id), "name": text.strip()}

            # if str(id) != self.last_id:x
            #     print(f"Producto leído: ID={id}, Nombre={text.strip()}")
            #     self.last_id = str(id)
            #     return {"id": str(id), "name": text.strip()}
        except Exception as e:
            print(f"Error leyendo producto: {e}")
            raise
        finally:
            GPIO.cleanup()

    def read_card(self):
        GPIO.setwarnings(False)
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

    def close(self):
        print("[RFID] Cerrando GPIO")
        GPIO.cleanup()
