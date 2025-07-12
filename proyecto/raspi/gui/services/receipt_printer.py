import os
import subprocess
from datetime import datetime
from typing import Optional

import requests

try:
    from gui.api.constants import BASE_URL  # Ruta estándar dentro del proyecto
except ModuleNotFoundError:
    # Fallback para entornos donde la ruta pueda variar
    BASE_URL = os.getenv("API_BASE_URL", "http://localhost/api/v1")


class ReceiptPrinter:
    """Servicio responsable de obtener la orden y enviar el comprobante a la impresora."""

    def __init__(self, printer_name: Optional[str] = None, api_base_url: str = BASE_URL):
        # Permitir definir impresora por variable de entorno o parámetro
        self.printer_name = printer_name or os.getenv("PRINTER_NAME")
        self.api_base_url = api_base_url.rstrip("/")  # Normalizar URL

    # ---------------------------------------------------------------------
    # API helpers
    # ---------------------------------------------------------------------
    def _fetch_order(self, order_id: int):
        """Obtiene la orden por ID. Devuelve el JSON o None si falla."""
        url = f"{self.api_base_url}/purchase-orders/{order_id}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            print(f"[RECEIPT_PRINTER] Error al obtener la orden {order_id}: {exc}")
            return None

    # ---------------------------------------------------------------------
    #  NUEVA IMPLEMENTACIÓN BASADA EN ARCHIVO DE TEXTO
    # ---------------------------------------------------------------------

    def _build_receipt_text(self, order: dict) -> str:
        """Genera un texto del ticket con más estilo (blanco y negro)."""
        width = 48  # ancho del ticket
        sep = "─" * width

        def center(text: str) -> str:
            return text.center(width)

        created_dt = None
        created_at = order.get("createdAt")
        if created_at:
            try:
                created_dt = datetime.fromisoformat(created_at)
            except ValueError:
                pass

        lines = [
            sep,
            center("AUTOCASHIER 2025"),
            center("COMPROBANTE DE COMPRA"),
            sep,
            f"ORDEN   : {order.get('id')}",
            f"ESTADO  : {order.get('status')}",
            f"FECHA   : {created_dt.strftime('%d/%m/%Y %H:%M:%S') if created_dt else '---'}",
            f"USUARIO : {order['user']['username']} ({order['user']['externalId']})",
            sep,
            f"{'PRODUCTO':<25}{'CANT':>5}{'P.UNIT':>8}{'SUBT':>10}",
            sep,
        ]

        for item in order.get("items", []):
            name = str(item.get("productName", ""))[:24]
            qty = str(item.get("quantity", 0))
            unit = f"{item.get('unitPrice', 0):.2f}"
            subtotal = f"{item.get('subtotal', 0):.2f}"
            lines.append(f"{name:<25}{qty:>5}{unit:>8}{subtotal:>10}")

        lines.extend([
            sep,
            f"TOTAL: {order.get('total', 0):.2f} ARS".rjust(width),
            sep,
            center("¡Gracias por tu compra!"),
            center("Visítanos nuevamente."),
            sep,
            "\n"  # Línea extra para alimentación
        ])

        return "\n".join(lines)

    def _generate_receipt_file(self, order: dict) -> str:
        """Escribe el recibo en un archivo temporal y devuelve la ruta."""
        text = self._build_receipt_text(order)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = f"/tmp/receipt_{order['id']}_{timestamp}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        return file_path

    def _print_file(self, file_path: str) -> bool:
        """Envía el archivo al spool de impresión."""
        command = ["lp"]
        if self.printer_name:
            command.extend(["-d", self.printer_name])
        command.append(file_path)
        try:
            result = subprocess.run(command, capture_output=True)
            if result.returncode == 0:
                print(f"[RECEIPT_PRINTER] Archivo enviado a la impresora: {file_path}")
                return True
            print(f"[RECEIPT_PRINTER] Error al imprimir archivo: {result.stderr.decode()}")
        except FileNotFoundError:
            print("[RECEIPT_PRINTER] Comando 'lp' no encontrado. ¿Está CUPS instalado?")
        except Exception as exc:
            print(f"[RECEIPT_PRINTER] Excepción al imprimir archivo: {exc}")
        return False

    # ---------------------------------------------------------------------
    # API pública
    # ---------------------------------------------------------------------
    def print_receipt(self, order_id: int) -> bool:
        """Obtiene la orden, crea el archivo y lo envía a imprimir."""
        order = self._fetch_order(order_id)
        if not order:
            return False

        if order.get("status") != "COMPLETED":
            print(
                f"[RECEIPT_PRINTER] La orden {order_id} no está completada (estado: {order.get('status')})."
            )
            return False

        # --- Nueva lógica basada en archivo ---
        receipt_file = self._generate_receipt_file(order)
        success = self._print_file(receipt_file)

        # Limpiar archivo si se imprimió correctamente
        if success:
            try:
                os.remove(receipt_file)
            except OSError:
                pass
        return success

# ---------------------------------------------------------------------
# IMPLEMENTACIÓN ORIGINAL (conservada íntegra para referencia)
# ---------------------------------------------------------------------
# def _format_receipt(self, order: dict) -> str:
#     """Devuelve un string listo para imprimir en blanco y negro."""
#     created_at = order.get("createdAt")
#     try:
#         created_dt = datetime.fromisoformat(created_at) if created_at else None
#     except ValueError:
#         created_dt = None
#
#     header_lines = [
#         "=" * 42,
#         "          AUTOCASHIER 2025",  # Título
#         "          COMPROBANTE DE COMPRA",
#         "=" * 42,
#     ]
#
#     info_lines = [
#         f"ORDEN  : {order.get('id')}",
#         f"ESTADO : {order.get('status')}",
#         (
#             f"FECHA  : {created_dt.strftime('%d/%m/%Y %H:%M:%S')}"
#             if created_dt
#             else "FECHA  : ---"
#         ),
#         f"USUARIO : {order['user']['username']} ({order['user']['externalId']})",
#         "-" * 42,
#         "PRODUCTO            CANT  PRECIO   SUBT",
#         "-" * 42,
#     ]
#
#     item_lines = []
#     for item in order.get("items", []):
#         name = str(item.get("productName", "")).ljust(18)[:18]
#         qty = str(item.get("quantity", 0)).rjust(4)
#         unit = f"{item.get('unitPrice', 0):.2f}".rjust(7)
#         subtotal = f"{item.get('subtotal', 0):.2f}".rjust(7)
#         item_lines.append(f"{name}{qty}{unit}{subtotal}")
#
#     total_line = [
#         "-" * 42,
#         f"TOTAL: {order.get('total', 0):.2f} ARS".rjust(42),
#         "-" * 42,
#     ]
#
#     footer_lines = [
#         "¡Gracias por tu compra!",  # Mensaje de despedida
#         "Visítanos nuevamente.",
#         "\n" * 3,  # Alimentar papel
#     ]
#
#     return "\n".join(
#         header_lines + info_lines + item_lines + total_line + footer_lines
#     )
#
# def _send_to_printer(self, receipt_text: str) -> bool:
#     """Envía el texto formateado a la impresora mediante lp/lpr."""
#     command = ["lp"]
#     if self.printer_name:
#         command.extend(["-d", self.printer_name])
#     try:
#         result = subprocess.run(
#             command, input=receipt_text.encode(), capture_output=True
#         )
#         if result.returncode == 0:
#             print("[RECEIPT_PRINTER] Comprobante enviado a la impresora.")
#             return True
#         error_msg = result.stderr.decode()
#         print(f"[RECEIPT_PRINTER] Error al imprimir: {error_msg}")
#     except FileNotFoundError:
#         print("[RECEIPT_PRINTER] Comando 'lp' no encontrado. ¿Está CUPS instalado?")
#     except Exception as exc:
#         print(f"[RECEIPT_PRINTER] Excepción al imprimir: {exc}")
#     return False 