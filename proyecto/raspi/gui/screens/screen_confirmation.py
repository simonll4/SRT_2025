import tkinter as tk
from tkinter import messagebox, ttk
from gui.view_models.product_view_model import ProductViewModel
from gui.screens.screen_purchase_result import PurchaseResultScreen


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

        # Para órdenes fallidas, solo actualizamos localmente
        if self.order["status"] == "FAILED":
            if product["quantity"] > 1:
                product["quantity"] -= 1
            else:
                self.last_products.pop(index)
            return

        # Para órdenes no fallidas, actualizamos en la API
        try:
            original_item = self._find_matching_order_item(product["name"])
            if not original_item:
                print(f"No se encontró el item original para {product['name']}")
                return

            if "productId" not in original_item:
                print(
                    f"Estructura de producto inválida en el item original: {original_item}"
                )
                return

            update_data = self._prepare_update_data(product, original_item)
            if not update_data:
                return

            if self._process_product_update(product, update_data):
                self.refresh_screen()

        except Exception as e:
            print(f"Error al eliminar producto: {e}")
            messagebox.showerror(
                "Error", "No se pudo actualizar la orden en el servidor"
            )

    def _find_matching_order_item(self, product_name):
        """Encuentra el item de la orden que coincide con el producto."""
        return next(
            (
                item
                for item in self.order["items"]
                if item["productName"].lower() == product_name.lower()
            ),
            None,
        )

    def _prepare_update_data(self, product, original_item):
        """Prepara los datos para actualizar el producto."""
        new_quantity = product["quantity"] - 1
        if new_quantity < 0:
            return None

        return {
            "item_id": original_item["id"],  # ID del item específico
            "product_id": original_item["productId"],
            "quantity": new_quantity,
        }

    def _process_product_update(self, product, update_data):
        """Procesa la actualización del producto y actualiza la lista local."""
        success = self.product_viewmodel.update_order_items(
            self.order["id"], [update_data]
        )

        if not success:
            return False

        if update_data["quantity"] == 0:
            self.last_products.remove(product)
        else:
            product["quantity"] = update_data["quantity"]

        return True

    def refresh_screen(self):
        """Vuelve a renderizar los widgets para reflejar los cambios."""
        new_total = sum(p["quantity"] * 100 for p in self.last_products)
        # Si no hay productos o el total es cero, finalizar automáticamente
        if not self.last_products or new_total <= 0:
            self.handle_zero_total()
            return
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

    def handle_zero_total(self):
        """Maneja el caso cuando no hay productos o el total es cero"""
        if self.order and "id" in self.order:
            # Si ya existe una orden, la marcamos como completada (o cancelada según tu lógica)
            success = self.product_viewmodel.order_service.complete_purchase_order(
                self.order["id"]
            )
        else:
            success = True  # Si no hay orden creada, consideramos éxito

        # Mostrar pantalla de resultado
        self.master.show_screen(
            PurchaseResultScreen,
            success=success,
            message=(
                "No hay productos para comprar"
                if not self.last_products
                else "El total de la compra es cero"
            ),
            user_data=self.user_data,
            on_return=self.on_logout,
        )

    def finalize_purchase(self):
        print("[INFO] Compra finalizada.")

        success = self.product_viewmodel.order_service.complete_purchase_order(
            self.order["id"]
        )

        if success:
            print("Orden completada exitosamente")
            # Mostrar pantalla de éxito
            self.master.show_screen(
                PurchaseResultScreen,
                success=True,
                message="Tu compra se ha completado con éxito",
                user_data=self.user_data,
                on_return=self.on_logout,
            )
        else:
            print("Error al completar la orden")
            # Mostrar pantalla de error
            self.master.show_screen(
                PurchaseResultScreen,
                success=False,
                message="Hubo un problema al procesar tu compra",
                user_data=self.user_data,
                on_return=self.on_logout,
            )

    def cancel_purchase(self):
        # Primera confirmación
        confirm = messagebox.askyesno(
            "Confirmar cancelación", "¿Estás seguro de cancelar la compra?"
        )
        if not confirm:
            return

        print("[INFO] Compra cancelada.")

        # Marcar la orden como cancelada en el backend si existe
        if self.order and "id" in self.order:
            try:
                success = self.product_viewmodel.cancel_order(self.order["id"])
                if success:
                    print("Orden cancelada exitosamente en el servidor")
                else:
                    print("Error al cancelar la orden en el servidor")
            except Exception as e:
                print(f"Error al cancelar orden: {e}")

        # Mostrar pantalla de resultado de cancelación
        self.master.show_screen(
            PurchaseResultScreen,
            success=False,  # Usamos False para indicar cancelación
            message="La compra ha sido cancelada exitosamente",
            user_data=self.user_data,
            on_return=self.on_logout,  # Después del timeout, hace logout
        )
