import tkinter as tk
from tkinter import messagebox, ttk, font as tkfont
import math
import time
from gui.view_models.product_view_model import ProductViewModel
from gui.screens.screen_purchase_result import PurchaseResultScreen
from gui.services.receipt_printer import ReceiptPrinter


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
        self.configure(bg="#f8f9fa")
        self.master = master
        self.order = order
        self.user_data = user_data
        self.total_amount = total_amount
        self.on_success = on_success
        self.on_failure = on_failure
        self.on_logout = on_logout

        self.product_viewmodel = ProductViewModel()
        self.last_products = products
        
        # Crear fuentes personalizadas más elegantes
        self.title_font = tkfont.Font(family="Segoe UI", size=28, weight="bold")
        self.subtitle_font = tkfont.Font(family="Segoe UI", size=20, weight="normal")
        self.text_font = tkfont.Font(family="Segoe UI", size=14, weight="normal")
        self.button_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.total_font = tkfont.Font(family="Segoe UI", size=24, weight="bold")
        self.small_font = tkfont.Font(family="Segoe UI", size=11, weight="normal")
        
        # Variables para animaciones
        self.animation_running = True
        self.pulse_alpha = 0
        
        # Configurar estilo para la tabla
        self.configure_table_style()
        self.create_widgets()
        
        # Iniciar animaciones
        self.animate_background()

    def configure_table_style(self):
        """Configura estilos ultra modernos para la tabla"""
        style = ttk.Style()
        
        # Estilo para el encabezado con gradiente simulado
        style.configure(
            "Modern.Treeview.Heading",
            font=('Segoe UI', 13, 'bold'),
            background="#2c3e50",
            foreground="#ecf0f1",
            padding=[15, 12],
            relief="flat"
        )
        
        # Estilo para las filas con mejor espaciado
        style.configure(
            "Modern.Treeview",
            font=('Segoe UI', 12),
            rowheight=50,
            background="#ffffff",
            fieldbackground="#ffffff",
            borderwidth=0,
            relief="flat"
        )
        
        # Estilo para filas seleccionadas con efecto suave
        style.map(
            "Modern.Treeview",
            background=[('selected', '#3498db')],
            foreground=[('selected', '#ffffff')]
        )
        
        # Estilo para la scrollbar moderna
        style.configure(
            "Modern.Vertical.TScrollbar",
            background="#bdc3c7",
            troughcolor="#ecf0f1",
            borderwidth=0,
            arrowcolor="#7f8c8d",
            darkcolor="#95a5a6",
            lightcolor="#95a5a6"
        )

    def create_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        # Canvas principal con fondo animado
        self.bg_canvas = tk.Canvas(self, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Contenedor principal con scroll ultra suave
        self.canvas = tk.Canvas(self, bg="#f8f9fa", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview, style="Modern.Vertical.TScrollbar")
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f8f9fa")

        # Configurar el scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Empaquetar canvas y scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Configurar el ancho del scrollable_frame
        self.canvas.bind("<Configure>", self.configure_scrollable_frame)
        self.bind_mousewheel()
            
        # Contenedor principal con sombra y bordes redondeados simulados
        main_container = tk.Frame(self.scrollable_frame, bg="#ffffff")
        main_container.pack(expand=True, fill="both", padx=25, pady=25)
        
        # Crear efecto de sombra con múltiples frames
        shadow_frame = tk.Frame(self.scrollable_frame, bg="#d5d8dc", height=3)
        shadow_frame.place(in_=main_container, x=3, y=3, relwidth=1, relheight=1)
        main_container.lift()
        
        # Encabezado con gradiente y iconos
        header_frame = tk.Frame(main_container, bg="#2c3e50", height=80)
        header_frame.pack(fill="x", pady=(0, 25))
        header_frame.pack_propagate(False)
        
        # Canvas para efectos en el header
        header_canvas = tk.Canvas(header_frame, bg="#2c3e50", highlightthickness=0, height=80)
        header_canvas.pack(fill="both", expand=True)
        
        # Crear gradiente en el header
        self.create_gradient(header_canvas, "#2c3e50", "#34495e")
        
        # Título con icono
        title_frame = tk.Frame(header_canvas, bg="#2c3e50")
        title_frame.place(relx=0.02, rely=0.5, anchor="w")
        
        # Icono de carrito de compras (simulado con canvas)
        cart_canvas = tk.Canvas(title_frame, width=40, height=40, bg="#2c3e50", highlightthickness=0)
        cart_canvas.pack(side="left", padx=(0, 15))
        self.draw_cart_icon(cart_canvas)
        
        tk.Label(
            title_frame, 
            text="Resumen de Compra", 
            font=self.title_font,
            bg="#2c3e50",
            fg="#ecf0f1"
        ).pack(side="left")
        
        # Información del usuario con estilo moderno
        user_frame = tk.Frame(header_canvas, bg="#2c3e50")
        user_frame.place(relx=0.98, rely=0.5, anchor="e")
        
        # Avatar simulado
        avatar_canvas = tk.Canvas(user_frame, width=35, height=35, bg="#2c3e50", highlightthickness=0)
        avatar_canvas.pack(side="right", padx=(15, 0))
        self.draw_avatar(avatar_canvas)
        
        user_info = tk.Label(
            user_frame,
            text=f"👤 {self.user_data.get('nombre', 'Usuario')}",
            font=self.text_font,
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        user_info.pack(side="right")
        
        # Mensaje de estado elegante para órdenes fallidas
        if self.order["status"] == "FAILED":
            alert_frame = tk.Frame(main_container, bg="#fff5f5")
            alert_frame.pack(fill="x", pady=(0, 20), padx=20)
            
            # Borde izquierdo colorido
            border_frame = tk.Frame(alert_frame, bg="#e53e3e", width=4)
            border_frame.pack(side="left", fill="y")
            
            content_frame = tk.Frame(alert_frame, bg="#fff5f5")
            content_frame.pack(side="left", fill="both", expand=True, padx=15, pady=15)
            
            # Icono de advertencia elegante
            warning_canvas = tk.Canvas(content_frame, width=24, height=24, bg="#fff5f5", highlightthickness=0)
            warning_canvas.pack(side="left", padx=(0, 12))
            self.draw_warning_icon(warning_canvas)
            
            tk.Label(
                content_frame,
                text="⚠️ Saldo insuficiente. Elimina algunos productos para continuar.",
                font=self.text_font,
                bg="#fff5f5",
                fg="#c53030"
            ).pack(side="left", anchor="w")

        # Contenedor de tabla con diseño moderno
        table_container = tk.Frame(main_container, bg="#ffffff")
        table_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Título de la sección
        section_title = tk.Label(
            table_container,
            text="📋 Productos Seleccionados",
            font=self.subtitle_font,
            bg="#ffffff",
            fg="#2c3e50"
        )
        section_title.pack(anchor="w", pady=(0, 15))
        
        # Frame para la tabla con borde elegante
        table_frame = tk.Frame(table_container, bg="#ffffff")
        table_frame.pack(fill="both", expand=True)
        
        # Crear borde redondeado simulado
        border_canvas = tk.Canvas(table_frame, bg="#ffffff", highlightthickness=0, height=2)
        border_canvas.pack(fill="x")
        border_canvas.create_rectangle(0, 0, 1000, 2, fill="#e1e8ed", outline="")

        # Tabla con estilo moderno
        columns = ("product", "quantity", "subtotal", "actions")
        self.tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show="headings", 
            height=6,
            style="Modern.Treeview"
        )
        
        # Configurar encabezados con iconos
        self.tree.heading("product", text="🛍️ Producto")
        self.tree.heading("quantity", text="📦 Cantidad")
        self.tree.heading("subtotal", text="💰 Subtotal")
        self.tree.heading("actions", text="⚙️ Acciones")
        
        # Configurar anchos optimizados
        self.tree.column("product", width=200, minwidth=150)
        self.tree.column("quantity", width=100, anchor=tk.CENTER, minwidth=80)
        self.tree.column("subtotal", width=120, anchor=tk.CENTER, minwidth=100)
        self.tree.column("actions", width=120, anchor=tk.CENTER, minwidth=100)
        
        # Scrollbar para la tabla
        table_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview, style="Modern.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=table_scrollbar.set)
        
        # Empaquetar tabla y scrollbar
        self.tree.pack(side=tk.LEFT, fill="both", expand=True, pady=10)
        table_scrollbar.pack(side=tk.RIGHT, fill="y")
        
        # Llenar la tabla con productos (TU LÓGICA ORIGINAL)
        for idx, item in enumerate(self.last_products):
            # Buscar el item correspondiente en la orden para obtener el precio unitario
            order_item = next(
                (order_item for order_item in self.order["items"] 
                 if order_item["productName"] == item["name"]),
                None
            )
            
            if order_item:
                subtotal = item["quantity"] * order_item["unitPrice"]
            else:
                # Fallback por si no se encuentra el item en la orden
                subtotal = item["quantity"] * 100
                
            self.tree.insert(
                "",
                tk.END,
                iid=str(idx),
                values=(
                    f"  {item['name']}",
                    f"×{item['quantity']}",
                    f"${subtotal:.2f}",
                    "🗑️ Eliminar",
                ),
                tags=("product_row",)
            )
        
        # Configurar tags para filas alternas
        self.tree.tag_configure("product_row", background="#fdfdfd")
        self.tree.bind("<Button-1>", self.handle_tree_click)
        
        # Panel de resumen con diseño premium
        summary_frame = tk.Frame(main_container, bg="#f8f9fa")
        summary_frame.pack(fill="x", padx=20, pady=20)
        
        # Crear gradiente sutil en el fondo
        summary_canvas = tk.Canvas(summary_frame, bg="#f8f9fa", highlightthickness=0, height=80)
        summary_canvas.pack(fill="both", expand=True)
        
        # Estadísticas de productos
        stats_frame = tk.Frame(summary_canvas, bg="#f8f9fa")
        stats_frame.place(relx=0.02, rely=0.5, anchor="w")
        
        total_items = sum(p['quantity'] for p in self.last_products)
        unique_products = len(self.last_products)
        
        tk.Label(
            stats_frame,
            text=f"📊 {unique_products} productos únicos • {total_items} artículos totales",
            font=self.small_font,
            bg="#f8f9fa",
            fg="#7f8c8d"
        ).pack()
        
        # Total con animación (TU LÓGICA ORIGINAL)
        total = sum(
            item["quantity"] * next(
                (order_item["unitPrice"] for order_item in self.order["items"] 
                 if order_item["productName"] == item["name"]),
                100  # Fallback por si no se encuentra el item
            )
            for item in self.last_products
        )
        self.total_amount = total
        
        # Frame para el total con efecto especial
        total_display_frame = tk.Frame(summary_canvas, bg="#f8f9fa")
        total_display_frame.place(relx=0.98, rely=0.5, anchor="e")
        
        tk.Label(
            total_display_frame,
            text="Total a pagar:",
            font=self.text_font,
            bg="#f8f9fa",
            fg="#7f8c8d"
        ).pack()
        
        self.total_label = tk.Label(
            total_display_frame,
            text=f"${self.total_amount:.2f}",
            font=self.total_font,
            bg="#f8f9fa",
            fg="#27ae60"
        )
        self.total_label.pack()
        
        # Botones con diseño ultra moderno
        btn_container = tk.Frame(main_container, bg="#ffffff")
        btn_container.pack(fill="x", padx=20, pady=(20, 30))
        
        # Frame para centrar botones
        btn_frame = tk.Frame(btn_container, bg="#ffffff")
        btn_frame.pack(anchor="center")
        
        # Botón de finalizar compra con gradiente
        self.finalize_btn = self.create_modern_button(
            btn_frame, 
            text="✅ Finalizar Compra", 
            bg_color="#27ae60",
            hover_color="#2ecc71",
            command=self.finalize_purchase
        )
        self.finalize_btn.grid(row=0, column=0, padx=12, pady=5)
        
        # Deshabilitar botón si la orden falló
        if self.order["status"] == "FAILED":
            self.finalize_btn.config(state=tk.DISABLED, bg="#95a5a6", activebackground="#95a5a6")
            
            # Botón de reintentar
            retry_btn = self.create_modern_button(
                btn_frame, 
                text="🔄 Reintentar Compra", 
                bg_color="#3498db",
                hover_color="#5dade2",
                command=self.retry_purchase
            )
            retry_btn.grid(row=0, column=1, padx=12, pady=5)
        
        # Botón de cancelar
        cancel_btn = self.create_modern_button(
            btn_frame, 
            text="❌ Cancelar", 
            bg_color="#e74c3c",
            hover_color="#ec7063",
            command=self.cancel_purchase
        )
        cancel_btn.grid(row=0, column=2, padx=12, pady=5)

    def create_modern_button(self, parent, text, bg_color, hover_color, command):
        """Crea un botón moderno con efectos hover"""
        btn = tk.Button(
            parent,
            text=text,
            font=self.button_font,
            bg=bg_color,
            fg="#ffffff",
            activebackground=hover_color,
            activeforeground="#ffffff",
            padx=25,
            pady=12,
            border=0,
            cursor="hand2",
            command=command,
            relief="flat"
        )
        
        # Efectos hover
        def on_enter(e):
            btn.config(bg=hover_color)
        
        def on_leave(e):
            btn.config(bg=bg_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

    def create_gradient(self, canvas, color1, color2):
        """Crea un gradiente vertical en el canvas"""
        canvas.update_idletasks()
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width > 1 and height > 1:
            # Crear gradiente con líneas
            for i in range(height):
                ratio = i / height
                r1, g1, b1 = self.hex_to_rgb(color1)
                r2, g2, b2 = self.hex_to_rgb(color2)
                
                r = int(r1 + (r2 - r1) * ratio)
                g = int(g1 + (g2 - g1) * ratio)
                b = int(b1 + (b2 - b1) * ratio)
                
                color = f"#{r:02x}{g:02x}{b:02x}"
                canvas.create_line(0, i, width, i, fill=color)

    def hex_to_rgb(self, hex_color):
        """Convierte color hex a RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def draw_cart_icon(self, canvas):
        """Dibuja un icono de carrito de compras"""
        canvas.create_rectangle(8, 15, 32, 28, outline="#ecf0f1", width=2, fill="")
        canvas.create_line(12, 28, 12, 32, fill="#ecf0f1", width=2)
        canvas.create_line(28, 28, 28, 32, fill="#ecf0f1", width=2)
        canvas.create_oval(10, 30, 14, 34, fill="#ecf0f1")
        canvas.create_oval(26, 30, 30, 34, fill="#ecf0f1")
        canvas.create_line(5, 12, 8, 15, fill="#ecf0f1", width=2)

    def draw_avatar(self, canvas):
        """Dibuja un avatar simple"""
        canvas.create_oval(5, 5, 30, 30, fill="#3498db", outline="#2980b9", width=2)
        canvas.create_oval(12, 12, 23, 20, fill="#ffffff")
        canvas.create_arc(10, 18, 25, 30, start=0, extent=180, fill="#ffffff")

    def draw_warning_icon(self, canvas):
        """Dibuja un icono de advertencia"""
        canvas.create_polygon(12, 4, 20, 20, 4, 20, fill="#e53e3e", outline="")
        canvas.create_text(12, 15, text="!", font=("Arial", 10, "bold"), fill="#ffffff")

    def animate_background(self):
        """Anima el fondo con partículas sutiles"""
        if not self.animation_running:
            return
            
        try:
            self.bg_canvas.delete("particles")
            
            # Crear partículas flotantes sutiles
            width = self.bg_canvas.winfo_width()
            height = self.bg_canvas.winfo_height()
            
            if width > 1 and height > 1:
                time_offset = time.time() * 0.5
                
                for i in range(8):
                    x = (i * width / 8 + math.sin(time_offset + i) * 30) % width
                    y = (math.sin(time_offset * 0.7 + i * 0.5) * height * 0.3 + height * 0.5) % height
                    size = 3 + math.sin(time_offset + i) * 1
                    
                    alpha = int(50 + math.sin(time_offset + i) * 30)
                    color = f"#{alpha:02x}{alpha:02x}{alpha + 20:02x}"
                    
                    self.bg_canvas.create_oval(
                        x - size, y - size, x + size, y + size,
                        fill=color, outline="", tags="particles"
                    )
            
            self.after(100, self.animate_background)
        except tk.TclError:
            pass

    def configure_scrollable_frame(self, event):
        """Ajusta el ancho del scrollable_frame al ancho del canvas"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw"), width=canvas_width)

    def bind_mousewheel(self):
        """Habilita scroll con rueda del mouse"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)

    # TODA TU LÓGICA ORIGINAL SE MANTIENE INTACTA
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
            try:
                ReceiptPrinter(printer_name="Samsung_ML-2950_Series").print_receipt(self.order["id"])
            except Exception as e:
                print(f"Error imprimiendo comprobante: {e}")
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

    def destroy(self):
        """Limpieza al cerrar la pantalla"""
        self.animation_running = False
        super().destroy()