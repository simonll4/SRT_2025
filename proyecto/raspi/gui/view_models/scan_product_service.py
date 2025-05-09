import requests
import mmap
import os

from gui.api.constants import BASE_URL
from gui.constants import SHM_NAME, SHM_SIZE


class ProductScanService:
    def __init__(self, api_base_url=BASE_URL):
        self.api_base_url = api_base_url
        self.scanned_products = []
        self.scanned_ids = set()

        # Configurar memoria compartida como solo lectura
        self.shm_fd = os.open(f"/dev/shm{SHM_NAME}", os.O_RDONLY)
        self.shm = mmap.mmap(self.shm_fd, SHM_SIZE * 2, access=mmap.ACCESS_READ)

    def read_shared_memory(self):
        """Lee los datos de la memoria compartida y los devuelve como diccionario."""
        try:
            # Leer ID (primeros SHM_SIZE bytes)
            self.shm.seek(0)
            id_data = self.shm.read(SHM_SIZE).split(b"\x00")[0]
            product_id = int(id_data.decode("utf-8")) if id_data else None

            # Leer nombre (siguientes SHM_SIZE bytes)
            self.shm.seek(SHM_SIZE)
            name_data = self.shm.read(SHM_SIZE).split(b"\x00")[0]
            product_name = name_data.decode("utf-8").strip() if name_data else ""

            return {"id": product_id, "name": product_name}

        except Exception as e:
            print(f"Error leyendo memoria compartida: {e}")
            return None

    def scan_product(self):
        """Escanea un producto y lo agrega solo si no ha sido escaneado antes (mismo ID)."""
        product_data = self.read_shared_memory()
        print(f"Datos leídos de memoria compartida: {product_data}")

        uid = product_data["id"]
        name = product_data["name"]

        # Validación del nombre
        if not name or not any(char.isalpha() for char in name):
            print("Nombre del producto no válido.")
            return None

        # Caso 1: ID ya escaneado → no hacer nada
        if uid in self.scanned_ids:
            print(f"Producto con ID {uid} ya escaneado. No se agregará nuevamente.")
            return None

        # Caso 2: Nombre repetido pero ID nuevo → agregar como nuevo producto
        for product in self.scanned_products:
            if product["name"] == name:
                print(
                    f"Nombre '{name}' repetido con nuevo ID {uid}. Se agregará como producto nuevo."
                )
                break

        # Caso 3: Producto nuevo → agregar
        new_product = {"id": uid, "name": name, "quantity": 1}
        self.scanned_products.append(new_product)
        self.scanned_ids.add(uid)
        return new_product

    def cleanup(self):
        """Libera recursos de memoria compartida."""
        if hasattr(self, "shm"):
            self.shm.close()
        if hasattr(self, "shm_fd"):
            os.close(self.shm_fd)

    def __del__(self):
        self.cleanup()

    def get_products(self):
        """Devuelve la lista actual de productos escaneados."""
        return self.scanned_products.copy()  # Copia para evitar modificaciones externas

    def build_order_payload(self, external_id):
        """Arma el JSON para enviar la orden (sin IDs en los productos)."""
        items = [
            {"product": {"product": product["name"]}, "quantity": product["quantity"]}
            for product in self.scanned_products
        ]
        return {"user": {"externalId": external_id}, "items": items}

    def send_order(self, external_id):
        """Envía la orden a la API."""
        payload = self.build_order_payload(external_id)
        print(f"Enviando orden: {payload}")
        try:
            response = requests.post(
                f"{self.api_base_url}/purchase-orders", json=payload
            )
            print(f"Respuesta de la API: {response.status_code} - {response.text}")
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            print(f"Error enviando la orden: {e}")
            return False
