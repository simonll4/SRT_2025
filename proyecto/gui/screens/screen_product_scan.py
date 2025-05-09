import tkinter as tk
from tkinter import ttk, messagebox
from gui.view_models.scan_product_service import ProductScanService
from gui.screens.screen_confirmation import ConfirmationScreen

# TODO: Sacar el precio de la tabla


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
        print("aca ta el objeto: ", user_data)
        self.on_success = on_success
        self.on_failure = on_failure
        self.on_cancel = on_cancel
        self.on_logout = on_logout

        self.scan_service = ProductScanService()

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Escaneo de Productos", font=("Arial", 18)).pack(pady=10)

        # Tabla de productos
        columns = ("name", "quantity", "price")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        self.tree.heading("name", text="Nombre del producto")
        self.tree.heading("quantity", text="Cantidad")
        self.tree.heading("price", text="Precio")

        self.tree.column("name", width=200)
        self.tree.column("quantity", width=100)
        self.tree.column("price", width=100)

        self.tree.pack(pady=10)

        # Botones de acción
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame, text="Escanear producto RFID", command=self.add_real_product
        ).grid(row=0, column=0, padx=5)
        tk.Button(
            btn_frame, text="Eliminar último producto", command=self.remove_last_product
        ).grid(row=0, column=1, padx=5)

        # Botones finales
        final_frame = tk.Frame(self)
        final_frame.pack(pady=20)

        tk.Button(
            final_frame, text="Finalizar compra", command=self.finalize_purchase
        ).grid(row=0, column=0, padx=10)
        tk.Button(
            final_frame, text="Cancelar compra", command=self.cancel_purchase
        ).grid(row=0, column=1, padx=10)

    def add_real_product(self):
        try:
            product = self.scan_service.scan_product()
            self.update_table()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo escanear el producto: {e}")

    def remove_last_product(self):
        # Esta función es opcional ahora, ya que los productos se gestionan por UID.
        messagebox.showinfo(
            "Aviso",
            "La eliminación manual no está implementada con escaneo RFID único.",
        )

    def update_table(self):
        self.tree.delete(*self.tree.get_children())
        for p in self.scan_service.get_products():
            self.tree.insert("", "end", values=(p["name"], p["quantity"]))

    def finalize_purchase(self):
        if not self.scan_service.get_products():
            messagebox.showwarning(
                "Sin productos", "Debe escanear al menos un producto."
            )
            return

        self.order = self.scan_service.send_order(self.user_data["external_id"])
        print("ORDER RECIBIDA: ", self.order)

        if self.order:

            total_amount = self.order["total"]
            self.master.show_screen(
                ConfirmationScreen,
                order=self.order,
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

    def cancel_purchase(self):
        confirm = messagebox.askyesno(
            "Cancelar compra", "¿Seguro que desea cancelar la compra?"
        )
        if confirm:
            self.on_logout()
