import requests
from gui.api.constants import BASE_URL
from gui.api.services.rfid_product_reader import RFIDProductReader


class ProductScanService:
    def __init__(self, api_base_url=BASE_URL):
        self.api_base_url = api_base_url
        self.reader = RFIDProductReader()
        self.scanned_products = {}

    def scan_product(self):
        """Escanea un producto y actualiza la lista de productos con cantidad."""
        product_data = self.reader.read_product()
        uid = product_data["id"]
        name = product_data["name"]

        if uid in self.scanned_products:
            self.scanned_products[uid]["quantity"] += 1
        else:
            self.scanned_products[uid] = {"name": name, "quantity": 1}

        return self.scanned_products[uid]

    def get_products(self):
        """Devuelve la lista actual de productos escaneados."""
        return list(self.scanned_products.values())

    def build_order_payload(self, external_id):
        """Arma el JSON para enviar la orden."""
        items = [
            {"product": {"product": data["name"]}, "quantity": data["quantity"]}
            for data in self.scanned_products.values()
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
                return  response.json()
        except requests.RequestException as e:
            print(f"Error enviando la orden: {e}")
            return False
