import tkinter as tk
import platform

from gui.screens.screen_identification import IdentificationScreen
from gui.screens.screen_welcome import WelcomeScreen
from gui.screens.screen_product_scan import ProductScanScreen
from gui.screens.screen_confirmation import ConfirmationScreen
from gui.view_models.auth_view_model import AuthViewModel
from gui.screens.screen_purchase_result import PurchaseResultScreen

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configuración inicial de la ventana
        self.setup_window()
        
        # Variables de estado
        self.is_fullscreen = False
        self.previous_geometry = None
        
        # Configuración global del servicio de autenticación
        self.auth_service = AuthViewModel()
        
        self.current_screen = None
        self.user_data = None
        self.order = None
        
        # Configurar eventos de teclado
        self.setup_keyboard_bindings()
        
        # Inicia directamente con identificación por RFID
        self.show_identification_screen()

    def setup_window(self):
        """Configura la ventana de manera adaptable"""
        self.title("AutoCashier")
        
        # Detectar el tamaño de la pantalla
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        print(f"[DISPLAY] Resolución detectada: {screen_width}x{screen_height}")
        
        # Calcular tamaño óptimo de ventana (80% de la pantalla)
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # Asegurar tamaño mínimo
        min_width = 1024
        min_height = 768
        
        if window_width < min_width:
            window_width = min_width
        if window_height < min_height:
            window_height = min_height
        
        # Si la pantalla es muy pequeña, usar pantalla completa por defecto
        if screen_width <= 1366 or screen_height <= 768:
            print("[DISPLAY] Pantalla pequeña detectada, iniciando en pantalla completa")
            self.start_fullscreen()
        else:
            # Centrar la ventana
            pos_x = (screen_width - window_width) // 2
            pos_y = (screen_height - window_height) // 2
            
            self.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
            self.minsize(min_width, min_height)
            self.resizable(True, True)
        
        # Configuración específica por sistema operativo
        self.setup_os_specific()
        
        print(f"[DISPLAY] Ventana configurada: {window_width}x{window_height}")

    def setup_os_specific(self):
        """Configuración específica según el sistema operativo"""
        system = platform.system()
        
        if system == "Windows":
            # Configuración para Windows
            self.iconbitmap(default="")  # Evitar errores de icono
            self.state('zoomed')  # Maximizar en Windows
            
        elif system == "Darwin":  # macOS
            # Configuración para macOS
            self.attributes('-zoomed', True)  # Maximizar en macOS
            
        elif system == "Linux":
            # Configuración para Linux
            try:
                self.attributes('-zoomed', True)  # Intentar maximizar
            except tk.TclError:
                # Si no funciona, usar pantalla completa
                self.start_fullscreen()
        
        print(f"[DISPLAY] Configuración aplicada para {system}")

    def setup_keyboard_bindings(self):
        """Configura los atajos de teclado"""
        # F11 para alternar pantalla completa
        self.bind('<F11>', lambda e: self.toggle_fullscreen())
        
        # Escape para salir de pantalla completa
        self.bind('<Escape>', lambda e: self.exit_fullscreen())
        
        # Alt+Enter para alternar pantalla completa (alternativo)
        self.bind('<Alt-Return>', lambda e: self.toggle_fullscreen())
        
        # Ctrl+Q para cerrar (Linux/Windows)
        self.bind('<Control-q>', lambda e: self.quit())
        
        # Cmd+Q para cerrar (macOS)
        self.bind('<Command-q>', lambda e: self.quit())
        
        print("[DISPLAY] Atajos de teclado configurados:")
        print("  F11 / Alt+Enter: Alternar pantalla completa")
        print("  Escape: Salir de pantalla completa")
        print("  Ctrl+Q / Cmd+Q: Cerrar aplicación")

    def start_fullscreen(self):
        """Inicia en modo pantalla completa"""
        self.previous_geometry = self.geometry()
        self.attributes('-fullscreen', True)
        self.is_fullscreen = True
        print("[DISPLAY] Modo pantalla completa activado")

    def toggle_fullscreen(self):
        """Alterna entre ventana y pantalla completa"""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()

    def enter_fullscreen(self):
        """Entra en modo pantalla completa"""
        if not self.is_fullscreen:
            self.previous_geometry = self.geometry()
            self.attributes('-fullscreen', True)
            self.is_fullscreen = True
            print("[DISPLAY] Entrando en pantalla completa")

    def exit_fullscreen(self):
        """Sale del modo pantalla completa"""
        if self.is_fullscreen:
            self.attributes('-fullscreen', False)
            self.is_fullscreen = False
            
            # Restaurar geometría anterior si existe
            if self.previous_geometry:
                self.geometry(self.previous_geometry)
            else:
                # Calcular nueva geometría centrada
                screen_width = self.winfo_screenwidth()
                screen_height = self.winfo_screenheight()
                window_width = int(screen_width * 0.8)
                window_height = int(screen_height * 0.8)
                pos_x = (screen_width - window_width) // 2
                pos_y = (screen_height - window_height) // 2
                self.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
            
            print("[DISPLAY] Saliendo de pantalla completa")

    def show_screen(self, screen_class, **kwargs):
        """Maneja la transición entre pantallas con mejor gestión de memoria"""
        # Limpiar pantalla anterior
        if self.current_screen:
            try:
                # Si la pantalla tiene método destroy personalizado, usarlo
                if hasattr(self.current_screen, 'destroy'):
                    self.current_screen.destroy()
                else:
                    self.current_screen.pack_forget()
            except tk.TclError:
                pass
        
        # Crear nueva pantalla
        self.current_screen = screen_class(self, **kwargs)
        self.current_screen.pack(fill="both", expand=True)
        
        # Forzar actualización de la interfaz
        self.update_idletasks()
        
        print(f"[SCREEN] Cambiando a: {screen_class.__name__}")

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

    def finalize_purchase(self, success, message):
        """Finaliza la compra y muestra el resultado"""
        self.show_screen(
            PurchaseResultScreen,
            success=success,
            message=message,
            user_data=self.user_data,
            on_return=self.show_identification_screen
        )

    def logout_user(self):
        """Cierra sesión y vuelve a identificación"""
        self.user_data = None
        self.order = None
        self.show_identification_screen()

    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        print("[APP] Cerrando aplicación...")
        
        # Limpiar pantalla actual
        if self.current_screen:
            try:
                if hasattr(self.current_screen, 'destroy'):
                    self.current_screen.destroy()
            except tk.TclError:
                pass
        
        # Cerrar aplicación
        self.quit()
        self.destroy()

    def run(self):
        """Inicia la aplicación con manejo de errores"""
        try:
            # Configurar protocolo de cierre
            self.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            print("[APP] Iniciando AutoCashier...")
            print(f"[APP] Modo pantalla completa: {self.is_fullscreen}")
            
            # Mostrar información de ayuda
            print("\n[AYUDA] Controles disponibles:")
            print("  F11 o Alt+Enter: Alternar pantalla completa")
            print("  Escape: Salir de pantalla completa")
            print("  Ctrl+Q: Cerrar aplicación")
            print()
            
            self.mainloop()
            
        except Exception as e:
            print(f"[ERROR] Error al iniciar la aplicación: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    app = App()
    app.run()
