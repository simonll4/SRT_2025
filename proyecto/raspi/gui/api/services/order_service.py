import requests

from gui.api.constants import BASE_URL


class PurchaseOrderService:
    def __init__(self, api_base_url=BASE_URL):
        self.api_base_url = api_base_url

    def complete_purchase_order(self, order_id):
        """
        Completa una orden de compra mediante su ID.

        Args:
            order_id (str): El ID de la orden de compra a completarA

        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        try:
            response = requests.post(
                f"{self.api_base_url}/purchase-orders/complete", json={"id": order_id}
            )
            print(f"Respuesta de la API: {response.status_code} - {response.text}")
            # Consideramos éxito cualquier código 2xx
            return response.ok

        except requests.RequestException as e:
            print(f"Error al completar la orden de compra: {e}")
            return False

    def send_purchase_order(self, external_id, scanned_products):
        """Envía la orden a la API."""
        payload = self.build_order_payload(external_id, scanned_products)
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

    def build_order_payload(self, external_id, scanned_products):
        """Arma el JSON para enviar la orden (sin IDs en los productos)."""
        items = [
            {"product": {"product": product["name"]}, "quantity": product["quantity"]}
            for product in scanned_products
        ]
        return {"user": {"externalId": external_id}, "items": items}

    def update_order_items(self, order_id, items):
        """
        Actualiza los items de una orden mediante PATCH
        
        Args:
            order_id (int): ID de la orden principal (no de los items)
            items (list): Lista de items con:
                - id: ID del item de orden
                - product_id: ID del producto
                - quantity: Nueva cantidad
                
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        try:
            payload = [
                {
                    "id": item["item_id"],  # ID del item específico
                    "order": {"id": order_id},  # ID de la orden principal
                    "product": {"id": item["product_id"]},
                    "quantity": item["quantity"]
                }
                for item in items
            ]
            
            response = requests.patch(
                f"{self.api_base_url}/purchase-orders/items",
                json=payload,
                timeout=5
            )
            
            print(f"Actualizando items: {payload}")
            print(f"Respuesta de la API: {response.status_code} - {response.text}")
            
            return response.ok
        except requests.RequestException as e:
            print(f"Error al actualizar items: {e}")
            return False