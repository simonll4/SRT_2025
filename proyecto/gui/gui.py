import tkinter as tk
import signal
import sys

from gui.screens.screen_identification import IdentificationScreen
from gui.screens.screen_welcome import WelcomeScreen
from gui.screens.screen_product_scan import ProductScanScreen
from gui.screens.screen_confirmation import ConfirmationScreen
from gui.api.services.auth_service import AuthService  # Importamos el servicio

# TODO: # def run_feedback(success):
#     command = ["sudo", "./rfid_feedback", "success" if success else "error"]
#     subprocess.run(command)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AutoCashier")
        self.geometry("1080x720")
        self.resizable(False, False)

        # Configuración global del servicio de autenticación
        self.auth_service = AuthService()

        self.current_screen = None
        self.user_data = None
        self.order = None

        # Inicia directamente con identificación por RFID
        self.show_identification_screen()

    def show_screen(self, screen_class, **kwargs):
        """Maneja la transición entre pantallas"""
        if self.current_screen:
            self.current_screen.destroy()
        self.current_screen = screen_class(self, **kwargs)
        self.current_screen.pack(fill="both", expand=True)

    def show_identification_screen(self):
        """Pantalla de identificación con RFID"""

        def on_success(user_data):
            print(f"[AUTH] Usuario autenticado: {user_data['nombre']}")
            print(user_data)
            self.user_data = user_data
            print(f"[AUTH] Datos del usuario (desde main.py): {self.user_data}")
            self.show_welcome_screen()

        def on_failure():
            print("[AUTH] Tarjeta no reconocida")
            # Mostrar mensaje de error y reintentar
            self.show_screen(
                IdentificationScreen,
                auth_service=self.auth_service,
                on_success=on_success,
                on_failure=on_failure,
            )

        self.show_screen(
            IdentificationScreen,
            auth_service=self.auth_service,
            on_success=on_success,
            on_failure=on_failure,
        )

    def show_welcome_screen(self):
        """Pantalla de bienvenida post-autenticación"""
        self.show_screen(
            WelcomeScreen,
            user_data=self.user_data,
            on_start_purchase=self.start_purchase,
            on_logout=self.logout_user,
        )

    def start_purchase(self):
        """Inicia el proceso de compra"""
        self.show_screen(
            ProductScanScreen,
            order=self.order,
            user_data=self.user_data,
            on_success=self.show_confirmation_screen,
            on_cancel=self.show_welcome_screen,
            on_failure=self.show_identification_screen,
            on_logout=self.logout_user,
        )

    def show_confirmation_screen(self, total_amount):
        """Pantalla de confirmación de pago"""
        self.show_screen(
            ConfirmationScreen,
            order=self.order,
            user_data=self.user_data,
            total_amount=total_amount,
            on_confirm=self.finalize_purchase,
            on_cancel=self.show_welcome_screen,
        )

    def finalize_purchase(self):
        """Lógica final de compra"""
        print(f"[PURCHASE] Compra finalizada por {self.user_data['nombre']}")
        # Aquí iría la lógica para registrar la transacción en el backend
        self.show_welcome_screen()

    def logout_user(self):
        """Cierra sesión y vuelve a identificación"""
        self.user_data = None
        self.show_identification_screen()


if __name__ == "__main__":
    app = App()
    app.mainloop()

