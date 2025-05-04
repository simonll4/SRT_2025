import tkinter as tk
from tkinter import ttk
from gui.screens.screen_confirmation import ConfirmationScreen

class ProductScanScreen(tk.Frame):
    def __init__(self, master, user_data, on_success, on_failure, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.user_data = user_data
        self.on_success = on_success
        self.on_failure = on_failure
        self.products = []
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

        # Botones de simulación
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Agregar producto simulado", command=self.add_mock_product).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Eliminar último producto", command=self.remove_last_product).grid(row=0, column=1, padx=5)

        # Botones finales
        final_frame = tk.Frame(self)
        final_frame.pack(pady=20)

        tk.Button(final_frame, text="Finalizar compra", command=self.finalize_purchase).grid(row=0, column=0, padx=10)
        tk.Button(final_frame, text="Cancelar compra", command=self.cancel_purchase).grid(row=0, column=1, padx=10)

    def add_mock_product(self):
        producto = {"name": "Producto X", "quantity": 1, "price": 123.45}
        self.products.append(producto)
        self.tree.insert("", "end", values=(producto["name"], producto["quantity"], f"${producto['price']:.2f}"))

    def remove_last_product(self):
        if self.products:
            self.products.pop()
            children = self.tree.get_children()
            if children:
                self.tree.delete(children[-1])

    def finalize_purchase(self):
        if not self.products:
            tk.messagebox.showwarning("Sin productos", "Debe agregar al menos un producto antes de finalizar.")
            return

        total_amount = sum(p["price"] * p["quantity"] for p in self.products)

        self.master.show_screen(
            ConfirmationScreen,
            user_data=self.user_data,
            total_amount=total_amount,
            on_success=self.on_success,
            on_failure=self.on_failure
        )

    def cancel_purchase(self):
        confirm = tk.messagebox.askyesno("Cancelar compra", "¿Seguro que desea cancelar la compra?")
        if confirm:
            self.master.show_screen(
                ConfirmationScreen,
                user_data=self.user_data,
                total_amount=0.0,
                on_success=self.on_success,
                on_failure=self.on_failure
            )
