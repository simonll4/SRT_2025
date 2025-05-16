import tkinter as tk
from tkinter import ttk
import threading
import time


class PurchaseResultScreen(tk.Frame):
    def __init__(
        self,
        master,
        success,
        message,
        user_data=None,
        on_return=None,
        *args,
        **kwargs,
    ):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.success = success
        self.message = message
        self.user_data = user_data
        self.on_return = on_return if on_return else lambda: None

        self.configure(bg="#f0f0f0")
        self.pack_propagate(False)

        self.create_widgets()
        self.start_countdown()

    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self, bg="#f0f0f0", padx=20, pady=40)
        main_frame.pack(expand=True, fill="both")

        # Icono de resultado
        icon = "✓" if self.success else "✗"
        icon_color = "#4CAF50" if self.success else "#F44336"

        tk.Label(
            main_frame,
            text=icon,
            font=("Arial", 72, "bold"),
            fg=icon_color,
            bg="#f0f0f0",
        ).pack(pady=(0, 20))

        # Mensaje principal
        tk.Label(
            main_frame,
            text="¡Compra exitosa!" if self.success else "¡Compra fallida!",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#333333",
        ).pack(pady=(0, 10))

        # Mensaje secundario
        tk.Label(
            main_frame,
            text=self.message,
            font=("Arial", 16),
            bg="#f0f0f0",
            fg="#555555",
            wraplength=600,
        ).pack(pady=(0, 30))

        # Información del usuario (si existe)
        if self.user_data:
            user_frame = tk.Frame(main_frame, bg="#e0e0e0", padx=15, pady=10)
            user_frame.pack(pady=(0, 30))

            tk.Label(
                user_frame,
                text=f"Usuario: {self.user_data.get('nombre', '')}",
                font=("Arial", 14),
                bg="#e0e0e0",
                fg="#333333",
            ).pack(anchor="w")

            tk.Label(
                user_frame,
                text=f"ID: {self.user_data.get('external_id', '')}",
                font=("Arial", 12),
                bg="#e0e0e0",
                fg="#555555",
            ).pack(anchor="w")

        # Contador regresivo
        self.countdown_label = tk.Label(
            main_frame,
            text="Volviendo en 5 segundos...",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#777777",
        )
        self.countdown_label.pack()

    def start_countdown(self, seconds=5):
        self.remaining = seconds
        self.update_countdown()

        # Iniciar hilo para el contador
        self.countdown_thread = threading.Thread(target=self.run_countdown, daemon=True)
        self.countdown_thread.start()

    def run_countdown(self):
        while self.remaining > 0:
            time.sleep(1)
            self.remaining -= 1
            self.countdown_label.after(0, self.update_countdown)

        # Cuando termina el contador, volver a la pantalla de identificación
        self.after(0, self.on_return)

    def update_countdown(self):
        self.countdown_label.config(text=f"Volviendo en {self.remaining} segundos...")
