import tkinter as tk
from tkinter import messagebox
from gui.screens.screen_identification import IdentificationScreen

class ConfirmationScreen(tk.Frame):
    def __init__(self, master, user_data, total_amount, on_success, on_failure, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.user_data = user_data
        self.total_amount = total_amount
        self.on_success = on_success
        self.on_failure = on_failure
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Resumen de la compra", font=("Arial", 18)).pack(pady=20)
        tk.Label(self, text=f"Total a pagar: ${self.total_amount:.2f}", font=("Arial", 16)).pack(pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=30)

        tk.Button(btn_frame, text="Finalizar compra", width=20, command=self.finalize_purchase).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Cancelar", width=20, command=self.cancel_purchase).grid(row=0, column=1, padx=10)

    def finalize_purchase(self):
        print("[INFO] Compra finalizada.")
        messagebox.showinfo("Compra finalizada", "Gracias por su compra.")
        self.master.show_screen(
            IdentificationScreen,
            on_success=self.on_success,
            on_failure=self.on_failure
        )

    def cancel_purchase(self):
        print("[INFO] Compra cancelada.")
        messagebox.showwarning("Compra cancelada", "Se ha cancelado la operación.")
        self.master.show_screen(
            IdentificationScreen,
            on_success=self.on_success,
            on_failure=self.on_failure
        )
