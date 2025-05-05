import tkinter as tk
from tkinter import ttk, messagebox
from gui.api.services.scan_product_service import ProductScanService
from gui.screens.screen_confirmation import ConfirmationScreen

# TODO: Sacar el precio de la tabla

class ProductScanScreen(tk.Frame):
    def __init__(
        self,
        master,
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
            self.tree.insert(
                "", "end", values=(p["name"], p["quantity"], f"${p['price']:.2f}")
            )

    def finalize_purchase(self):
        if not self.scan_service.get_products():
            messagebox.showwarning(
                "Sin productos", "Debe escanear al menos un producto."
            )
            return

        order = self.scan_service.send_order(self.user_data["external_id"])
        print("Orderrrrrrrrrrrrr: ", order)

        if order:
            
            # total_amount = sum(
            #     p["unitPrice"] * p["quantity"] for p in self.scan_service.get_products()
            # )
            total_amount = order["total"]
            self.master.show_screen(
                ConfirmationScreen,
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


# import tkinter as tk
# from tkinter import ttk
# from gui.screens.screen_confirmation import ConfirmationScreen

# class ProductScanScreen(tk.Frame):
#     def __init__(self, master, user_data, on_success, on_cancel, on_failure, on_logout, *args, **kwargs):
#         super().__init__(master, *args, **kwargs)
#         self.master = master
#         self.user_data = user_data
#         self.on_success = on_success
#         self.on_failure = on_failure
#         self.on_cancel = on_cancel
#         self.on_logout = on_logout
#         self.products = []
#         self.create_widgets()

#     def create_widgets(self):
#         tk.Label(self, text="Escaneo de Productos", font=("Arial", 18)).pack(pady=10)

#         # Tabla de productos
#         columns = ("name", "quantity", "price")
#         self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
#         self.tree.heading("name", text="Nombre del producto")
#         self.tree.heading("quantity", text="Cantidad")
#         self.tree.heading("price", text="Precio")

#         self.tree.column("name", width=200)
#         self.tree.column("quantity", width=100)
#         self.tree.column("price", width=100)

#         self.tree.pack(pady=10)

#         # Botones de simulación
#         btn_frame = tk.Frame(self)
#         btn_frame.pack(pady=10)

#         tk.Button(btn_frame, text="Agregar producto simulado", command=self.add_mock_product).grid(row=0, column=0, padx=5)
#         tk.Button(btn_frame, text="Eliminar último producto", command=self.remove_last_product).grid(row=0, column=1, padx=5)

#         # Botones finales
#         final_frame = tk.Frame(self)
#         final_frame.pack(pady=20)

#         tk.Button(final_frame, text="Finalizar compra", command=self.finalize_purchase).grid(row=0, column=0, padx=10)

#         tk.Button(final_frame, text="Cancelar compra", command=self.cancel_purchase).grid(row=0, column=1, padx=10)

#     # Cambiar por implementación real con la api
#     def add_mock_product(self):
#         producto = {"name": "Producto X", "quantity": 1, "price": 123.45}
#         self.products.append(producto)
#         self.tree.insert("", "end", values=(producto["name"], producto["quantity"], f"${producto['price']:.2f}"))

#     # Cambiar por implementación real con la api
#     def remove_last_product(self):
#         if self.products:
#             self.products.pop()
#             children = self.tree.get_children()
#             if children:
#                 self.tree.delete(children[-1])

#     # Cambiar por implementación real con la api
#     def finalize_purchase(self):
#         if not self.products:
#             tk.messagebox.showwarning("Sin productos", "Debe agregar al menos un producto antes de finalizar.")
#             return

#         total_amount = sum(p["price"] * p["quantity"] for p in self.products)

#         self.master.show_screen(
#             ConfirmationScreen,
#             user_data=self.user_data,
#             total_amount=total_amount,
#             on_success=self.on_success,
#             on_failure=self.on_failure,
#             on_logout=self.on_logout
#         )

#     def cancel_purchase(self):
#         confirm = tk.messagebox.askyesno("Cancelar compra", "¿Seguro que desea cancelar la compra?")
#         if confirm:
#             self.on_logout
