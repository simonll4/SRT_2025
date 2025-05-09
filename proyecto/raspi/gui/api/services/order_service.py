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
