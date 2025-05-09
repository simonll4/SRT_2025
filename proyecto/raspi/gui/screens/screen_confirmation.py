import tkinter as tk
from tkinter import messagebox, ttk
from gui.api.services.order_service import PurchaseOrderService
from gui.view_models.product_view_model import ProductViewModel


class ConfirmationScreen(tk.Frame):
    def __init__(
        self,
        master,
        order,
        products,
        user_data,
        total_amount,
        on_success,
        on_failure,
        on_logout,
        *args,
        **kwargs,
    ):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.order = order
        self.user_data = user_data
        self.total_amount = total_amount
        self.on_success = on_success
        self.on_failure = on_failure
        self.on_logout = on_logout

        self.product_viewmodel = ProductViewModel()
        self.last_products = products

        self.create_widgets()

    def create_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text="Resumen de la compra", font=("Arial", 18)).pack(pady=20)

        columns = ("product", "quantity", "subtotal", "actions")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=6)
        self.tree.heading("product", text="Producto")
        self.tree.heading("quantity", text="Cantidad")
        self.tree.heading("subtotal", text="Subtotal ($)")
        self.tree.heading("actions", text="Acción")
        self.tree.column("product", width=150)
        self.tree.column("quantity", width=80, anchor=tk.CENTER)
        self.tree.column("subtotal", width=100, anchor=tk.CENTER)
        self.tree.column("actions", width=100, anchor=tk.CENTER)

        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        for idx, item in enumerate(self.last_products):
            subtotal = item["quantity"] * 100
            self.tree.insert(
                "",
                tk.END,
                iid=str(idx),
                values=(
                    item["name"],
                    item["quantity"],
                    f"{subtotal:.2f}",
                    "Eliminar",
                ),
            )

            self.tree.pack(pady=10)

            self.tree.bind("<Button-1>", self.handle_tree_click)

            total = sum(p["quantity"] * 100 for p in self.last_products)
            self.total_amount = total
            tk.Label(
                self,
                text=f"Total a pagar: ${self.total_amount:.2f}",
                font=("Arial", 16),
            ).pack(pady=10)


        # Crear botones inferiores
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=30)
        
        if self.order["status"] == "FAILED":
            tk.Label(
                self,
                text="Saldo insuficiente. Elimina productos para continuar.",
                font=("Arial", 12),
                fg="red",
            ).pack(pady=5)

        self.finalize_btn = tk.Button(
            btn_frame,
            text="Finalizar compra",
            width=20,
            command=self.finalize_purchase,
        )
        self.finalize_btn.grid(row=0, column=0, padx=10)

        if self.order["status"] == "FAILED":
            self.finalize_btn.config(state=tk.DISABLED)
            tk.Button(
                btn_frame,
                text="Reintentar compra",
                width=20,
                command=self.retry_purchase,
            ).grid(row=0, column=1, padx=10)

        tk.Button(
            btn_frame, text="Cancelar", width=20, command=self.cancel_purchase
        ).grid(row=0, column=2, padx=10)

    def handle_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            row_id = self.tree.identify_row(event.y)
            col = self.tree.identify_column(event.x)

            if col == "#4":  # "actions" column
                self.remove_product(int(row_id))
                self.refresh_screen()

    def remove_product(self, index):
        """Elimina o decrementa el producto según su cantidad."""
        if index >= len(self.last_products):
            return

        product = self.last_products[index]
        if product["quantity"] > 1:
            product["quantity"] -= 1
        else:
            self.last_products.pop(index)

    def refresh_screen(self):
        """Vuelve a renderizar los widgets para reflejar los cambios."""
        self.create_widgets()

    def retry_purchase(self):
        """Reenvía la orden con productos modificados."""
        print("[INFO] Reintentando compra con productos:", self.last_products)

        response = self.product_viewmodel.send_order(
            self.user_data["external_id"], self.last_products
        )

        if response:
            print("Orden reenviada con éxito.")
            self.order = response  # Pisar con nueva orden
            self.refresh_screen()  # Refrescar interfaz
        else:
            print("Fallo al reenviar la orden.")
            messagebox.showerror("Error", "No se pudo reintentar la compra.")

    def finalize_purchase(self):
        print("[INFO] Compra finalizada.")
        messagebox.showinfo("Compra finalizada", "Gracias por su compra.")

        success = self.product_viewmodel.order_service.complete_purchase_order(
            self.order["id"]
        )
        if success:
            print("Orden completada exitosamente")
        else:
            print("Error al completar la orden")
        self.on_logout()

    def cancel_purchase(self):
        confirm = messagebox.askyesno(
            "Confirmar cancelación", "¿Estás seguro de cancelar la compra?"
        )
        if not confirm:
            return
        print("[INFO] Compra cancelada.")
        messagebox.showwarning("Compra cancelada", "Se ha cancelado la operación.")
        self.on_logout()


# import tkinter as tk
# from tkinter import messagebox, ttk
# from gui.api.services.order_service import PurchaseOrderService
# from gui.view_models.product_view_model import ProductViewModel

# # TODO: Mostrar el resumen de los productos junto con el subtotal y el total a pagar
# # TODO: Hacer doble confirmacion de la cancelacion de la compra


# class ConfirmationScreen(tk.Frame):
#     def __init__(
#         self,
#         master,
#         order,
#         user_data,
#         total_amount,
#         on_success,
#         on_failure,
#         on_logout,
#         *args,
#         **kwargs,
#     ):
#         super().__init__(master, *args, **kwargs)
#         self.order = order
#         self.user_data = user_data
#         self.total_amount = total_amount
#         self.on_success = on_success
#         self.on_failure = on_failure
#         self.on_logout = on_logout
#         self.order_service = PurchaseOrderService()

#         self.product_viewmodel = ProductViewModel()
#         self.last_products = self.product_viewmodel.get_products()

#         self.create_widgets()

#     def create_widgets(self):
#         tk.Label(self, text="Resumen de la compra", font=("Arial", 18)).pack(pady=20)

#         # Tabla tipo Treeview
#         columns = ("product", "quantity", "subtotal")
#         tree = ttk.Treeview(self, columns=columns, show="headings", height=6)
#         tree.heading("product", text="Producto")
#         tree.heading("quantity", text="Cantidad")
#         tree.heading("subtotal", text="Subtotal ($)")
#         tree.column("product", width=150)
#         tree.column("quantity", width=80, anchor=tk.CENTER)
#         tree.column("subtotal", width=100, anchor=tk.CENTER)

#         for item in self.order["items"]:
#             tree.insert("", tk.END, values=(item["productName"], item["quantity"], f"{item['subtotal']:.2f}"))

#         tree.pack(pady=10)

#         # Total
#         tk.Label(
#             self, text=f"Total a pagar: ${self.total_amount:.2f}", font=("Arial", 16)
#         ).pack(pady=10)

#         # Mensaje de saldo insuficiente
#         if self.order["status"] == "FAILED":
#             tk.Label(
#                 self, text="Saldo insuficiente. Elimina productos para continuar.",
#                 font=("Arial", 12), fg="red"
#             ).pack(pady=5)

#         # Botones
#         btn_frame = tk.Frame(self)
#         btn_frame.pack(pady=30)

#         self.finalize_btn = tk.Button(
#             btn_frame, text="Finalizar compra", width=20, command=self.finalize_purchase
#         )
#         self.finalize_btn.grid(row=0, column=0, padx=10)

#         # Habilita o deshabilita el botón según el estado
#         if self.order["status"] == "FAILED":
#             self.finalize_btn.config(state=tk.DISABLED)

#         tk.Button(
#             btn_frame, text="Cancelar", width=20, command=self.cancel_purchase
#         ).grid(row=0, column=1, padx=10)

#     def finalize_purchase(self):
#         print("[INFO] Compra finalizada.")
#         messagebox.showinfo("Compra finalizada", "Gracias por su compra.")

#         success = self.order_service.complete_purchase_order(self.order["id"])
#         if success:
#             print("Orden completada exitosamente")
#         else:
#             print("Error al completar la orden")
#         self.on_logout()

#     def cancel_purchase(self):
#         print("[INFO] Compra cancelada.")
#         messagebox.showwarning("Compra cancelada", "Se ha cancelado la operación.")
#         self.on_logout()
