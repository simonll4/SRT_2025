import requests
import mmap
import os
import posix_ipc

from gui.api.constants import BASE_URL
from gui.constants import SHM_NAME, SHM_SIZE, SEM_NAME
from gui.types.product_status import ProductScanStatus
from gui.api.services.order_service import PurchaseOrderService


class ProductViewModel:
    def __init__(self, api_base_url=BASE_URL):
        self.api_base_url = api_base_url
        self.scanned_products = []
        self.scanned_ids = set()

        self.order_service = PurchaseOrderService()

        # Configurar memoria compartida como solo lectura
        self.shm_fd = os.open(f"/dev/shm{SHM_NAME}", os.O_RDONLY)
        self.shm = mmap.mmap(self.shm_fd, SHM_SIZE * 2, access=mmap.ACCESS_READ)

    def read_shared_memory(self):
        """Lee los datos de la memoria compartida de forma segura usando semáforo."""
        try:
            sem = posix_ipc.Semaphore(SEM_NAME)
            sem.acquire(timeout=2)

            with open(f"/dev/shm{SHM_NAME}", "rb") as shm_file:
                with mmap.mmap(
                    shm_file.fileno(), SHM_SIZE * 2, access=mmap.ACCESS_READ
                ) as shm:
                    shm.seek(0)
                    id_data = shm.read(SHM_SIZE).split(b"\x00")[0]
                    product_id = int(id_data.decode("utf-8")) if id_data else None

                    shm.seek(SHM_SIZE)
                    name_data = shm.read(SHM_SIZE).split(b"\x00")[0]
                    product_name = (
                        name_data.decode("utf-8").strip() if name_data else ""
                    )

            sem.release()
            return {"id": product_id, "name": product_name}

        except posix_ipc.BusyError:
            print("Semáforo ocupado, no se pudo leer memoria compartida a tiempo.")
        except Exception as e:
            print(f"Error leyendo memoria compartida: {e}")
        return None

    def clear_shared_memory(self):
        """Limpia la memoria compartida de forma segura usando semáforo."""
        try:
            sem = posix_ipc.Semaphore(SEM_NAME)
            sem.acquire(timeout=2)

            with open(f"/dev/shm{SHM_NAME}", "r+b") as shm_file:
                with mmap.mmap(shm_file.fileno(), SHM_SIZE * 2) as shm:
                    shm.seek(0)
                    shm.write(b"\x00" * SHM_SIZE)
                    shm.seek(SHM_SIZE)
                    shm.write(b"\x00" * SHM_SIZE)

            sem.release()

        except posix_ipc.BusyError:
            print("Semáforo ocupado, no se pudo limpiar memoria compartida a tiempo.")
        except Exception as e:
            print(f"Error al limpiar memoria compartida: {e}")

    def scan_product(self):
        """Escanea un producto y lo agrega solo si no ha sido escaneado antes."""
        try:
            product_data = self.read_shared_memory()
            print(f"Datos leídos de memoria compartida: {product_data}")

            if not product_data:
                self.clear_shared_memory()
                return ProductScanStatus.ERROR, None

            uid = product_data["id"]
            name_raw = product_data["name"]

            if uid is None:
                self.clear_shared_memory()
                return ProductScanStatus.NO_PRODUCT, None

                # Limpieza del nombre
            name = (
                name_raw.encode("utf-8", "ignore")
                .decode("utf-8", "ignore")
                .strip()
                .replace("\x00", "")
            )
            name = "".join(c for c in name if c.isprintable())

            if not name or not any(char.isalpha() for char in name):
                self.clear_shared_memory()
                return ProductScanStatus.INVALID_NAME, None

            if uid in self.scanned_ids:
                self.clear_shared_memory()
                return ProductScanStatus.DUPLICATE, None

            # new_product = {"id": uid, "name": name, "quantity": 1}
            new_product = {"name": name, "quantity": 1}
            existing = next(
                (p for p in self.scanned_products if p["name"] == name), None
            )
            if existing:
                existing["quantity"] += 1
            else:
                self.scanned_products.append(new_product)

            # self.scanned_products.append(new_product)
            self.scanned_ids.add(uid)

            self.clear_shared_memory()
            return ProductScanStatus.SUCCESS, new_product

        except Exception as e:
            print(f"Error escaneando producto: {e}")
            return ProductScanStatus.ERROR, None

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

    def send_order(self, external_id, products):
        """Envía la orden a la API."""
        if not products:
            products = self.scanned_products
        return self.order_service.send_purchase_order(external_id, products)

    def update_order_items(self, order_id, items_to_update):
        """
        Actualiza los items de una orden mediante el servicio de ordenes

        Args:
            order_id (int): ID de la orden
            items_to_update (list): Lista de diccionarios con:
                - id: ID del item de la orden
                - product_id: ID del producto
                - quantity: Nueva cantidad

        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        return self.order_service.update_order_items(order_id, items_to_update)

    # En gui/view_models/product_view_model.py
    def cancel_order(self, order_id, description="ORDEN DE COMPRA CANCELADA"):
        """
        Cancela una orden mediante el servicio de órdenes

        Args:
            order_id (str): ID de la orden a cancelar
            description (str): Descripción opcional para la cancelación

        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        return self.order_service.cancel_order(order_id, description)
