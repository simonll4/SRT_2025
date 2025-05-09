import requests
from gui.api.constants import BASE_URL
from gui.services.rfid_reader import RFIDReader


class ProductScanService:
    def __init__(self, api_base_url=BASE_URL):
        self.api_base_url = api_base_url
        self.reader = RFIDReader()
        self.scanned_products = []
        self.scanned_ids = set()

    def scan_product(self):
        """Escanea un producto y lo agrega solo si no ha sido escaneado antes (mismo ID)."""
        product_data = self.reader.read_product()
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
