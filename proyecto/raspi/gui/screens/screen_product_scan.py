import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

from gui.view_models.product_view_model import ProductViewModel
from gui.screens.screen_confirmation import ConfirmationScreen


class ProductScanScreen(tk.Frame):
    def __init__(
        self,
        master,
        order,
        user_data,
        on_success,
        on_cancel,
        on_failure,
        on_logout,
        *args,
        **kwargs,
    ):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.order = order
        self.user_data = user_data
        self.on_success = on_success
        self.on_failure = on_failure
        self.on_cancel = on_cancel
        self.on_logout = on_logout

        self.product_viewmodel = ProductViewModel()
        self.scan_thread = None
        self.scan_active = False
        self.scan_lock = threading.Lock()

        self.create_widgets()
        self.start_scan_thread()

    def create_widgets(self):
        tk.Label(self, text="Escaneo de Productos", font=("Arial", 18)).pack(pady=10)

        # Tabla de productos
        columns = ("name", "quantity")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        self.tree.heading("name", text="Nombre del producto")
        self.tree.heading("quantity", text="Cantidad")

        self.tree.column("name", width=200)
        self.tree.column("quantity", width=100)

        self.tree.pack(pady=10)

        # Botones de acción
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        # Botones finales
        final_frame = tk.Frame(self)
        final_frame.pack(pady=20)

        tk.Button(
            final_frame, text="Aceptar compra", command=self.finalize_purchase
        ).grid(row=0, column=0, padx=10)
        tk.Button(
            final_frame, text="Cancelar compra", command=self.cancel_purchase
        ).grid(row=0, column=1, padx=10)

    def start_scan_thread(self):
        """Inicia el hilo de escaneo continuo"""
        self.scan_active = True
        self.scan_thread = threading.Thread(
            target=self.scan_products_continuously, daemon=True
        )
        self.scan_thread.start()

    def scan_products_continuously(self):
        """Hilo secundario que escanea productos continuamente"""
        # TODO: ver si se puede hacer la ejecucion con signals
        while self.scan_active:
            try:
                with self.scan_lock:
                    status, product = self.product_viewmodel.scan_product()
                    if product:
                        self.after(0, self.update_table)
            except Exception as e:
                self.after(
                    0, lambda: messagebox.showerror("Error", f"Error al escanear: {e}")
                )

            time.sleep(0.5)  # Pequeña pausa para no saturar

    def update_table(self):
        self.tree.delete(*self.tree.get_children())
        for p in self.product_viewmodel.get_products():
            name = p["name"]
            quantity = p["quantity"]
            self.tree.insert("", "end", values=(name, quantity))

    def stop_scan_thread(self):
        """Detiene el hilo de escaneo"""
        self.scan_active = False
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=1)

    def finalize_purchase(self):
        """Finaliza la compra y detiene el escaneo"""
        self.stop_scan_thread()

        if not self.product_viewmodel.get_products():
            messagebox.showwarning(
                "Sin productos", "Debe escanear al menos un producto."
            )
            self.start_scan_thread()  # Reanudar escaneo
            return

        self.order = self.product_viewmodel.send_order(
            self.user_data["external_id"], []
        )

        if self.order:
            total_amount = self.order["total"]
            self.master.show_screen(
                ConfirmationScreen,
                order=self.order,
                products=self.product_viewmodel.get_products(),
                user_data=self.user_data,
                total_amount=total_amount,
                on_success=self.on_success,
                on_failure=self.on_failure,
                on_logout=self.on_logout,
            )
        else:
            messagebox.showerror(
                "Error", "No se pudo enviar la orden. Intente de nuevo."
            )
            self.start_scan_thread()  # Reanudar escaneo

    def cancel_purchase(self):
        """Cancela la compra y detiene el escaneo"""
        confirm = messagebox.askyesno(
            "Cancelar compra", "¿Seguro que desea cancelar la compra?"
        )
        if confirm:
            self.stop_scan_thread()
            self.on_logout()

    def destroy(self):
        """Limpieza al cerrar la pantalla"""
        self.stop_scan_thread()
        super().destroy()
