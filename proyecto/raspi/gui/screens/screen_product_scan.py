import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import threading
import time
import math
import random
import socket

from gui.view_models.product_view_model import ProductViewModel
from gui.screens.screen_confirmation import ConfirmationScreen
from gui.screens.screen_purchase_result import PurchaseResultScreen
from gui.types.product_status import ProductScanStatus

# Ruta del socket para feedback de LEDs
SOCKET_PATH = "/tmp/gpio_feedback.sock"


def send_gpio_feedback(message: str):
    """Envía un mensaje (SUCCESS o FAILURE) al proceso de feedback GPIO"""
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(SOCKET_PATH)
            client.sendall(message.encode("utf-8"))
    except Exception as e:
        print(f"[GPIO_FEEDBACK] Error al enviar mensaje: {e}")


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
        self.configure(bg="#f8f9fa")
        self.master = master
        self.order = order
        self.user_data = user_data
        self.on_success = on_success
        self.on_failure = on_failure
        self.on_cancel = on_cancel
        self.on_logout = on_logout

        # Asegurar que este frame ocupe todo el espacio disponible
        self.pack(fill="both", expand=True)
        
        # Configurar grid para expansión
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.product_viewmodel = ProductViewModel()
        self.scan_thread = None
        self.scan_active = False
        self.scan_lock = threading.Lock()
        
        # Variables para animaciones
        self.animation_running = True
        self.scan_effect_pos = 0
        self.scan_effect_dir = 1
        self.scan_pulse = 0
        self.last_scan_time = time.time()
        self.scan_count = 0
        self.particles = []
        
        # Variables para el tiempo de escaneo
        self.scan_start_time = time.time()
        self.scan_timer_active = True

        # Crear fuentes personalizadas más elegantes
        self.title_font = tkfont.Font(family="Segoe UI", size=28, weight="bold")
        self.subtitle_font = tkfont.Font(family="Segoe UI", size=20, weight="normal")
        self.text_font = tkfont.Font(family="Segoe UI", size=14, weight="normal")
        self.button_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.small_font = tkfont.Font(family="Segoe UI", size=11, weight="normal")

        # Configurar estilo para la tabla
        self.configure_table_style()

        self.create_widgets()
        self.start_scan_thread()

        # Iniciar animaciones
        self.scanning_animation()
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
        # Canvas principal con fondo animado
        self.bg_canvas = tk.Canvas(self, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Contenedor principal con scroll ultra suave
        self.canvas = tk.Canvas(self, bg="#f8f9fa", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview, style="Modern.Vertical.TScrollbar")
        
        # Usar grid para posicionar canvas y scrollbar
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configurar el canvas para que use toda la altura disponible
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Crear frame scrollable dentro del canvas
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f8f9fa")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Hacer que el scrollable_frame tenga el ancho del canvas
        self.canvas.bind("<Configure>", self.configure_scrollable_frame)
        
        # Crear ventana en el canvas con el scrollable_frame
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        
        # Bind mousewheel para scroll con mouse
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
        
        # Icono de escaneo (simulado con canvas)
        scan_icon_canvas = tk.Canvas(title_frame, width=40, height=40, bg="#2c3e50", highlightthickness=0)
        scan_icon_canvas.pack(side="left", padx=(0, 15))
        self.draw_scan_icon(scan_icon_canvas)
        
        tk.Label(
            title_frame, 
            text="Escaneo de Productos", 
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

        # Contenedor para la tabla y animación de escaneo
        content_container = tk.Frame(main_container, bg="#ffffff", padx=20, pady=10)
        content_container.pack(fill="both", expand=True)
        
        # Panel de información de escaneo con diseño premium
        scan_info_frame = tk.Frame(content_container, bg="#f0f9ff", padx=20, pady=15)
        scan_info_frame.pack(fill="x", pady=(0, 20))
        
        # Borde izquierdo colorido
        border_frame = tk.Frame(scan_info_frame, bg="#3498db", width=4)
        border_frame.pack(side="left", fill="y")
        
        # Contenido del panel de información
        scan_content = tk.Frame(scan_info_frame, bg="#f0f9ff", padx=15)
        scan_content.pack(side="left", fill="both", expand=True)
        
        # Título del panel
        tk.Label(
            scan_content,
            text="🔍 Escaneando productos",
            font=self.subtitle_font,
            bg="#f0f9ff",
            fg="#2c3e50"
        ).pack(anchor="w", pady=(0, 5))
        
        # Descripción
        tk.Label(
            scan_content,
            text="Acerque los productos al lector RFID para escanearlos automáticamente.",
            font=self.small_font,
            bg="#f0f9ff",
            fg="#7f8c8d"
        ).pack(anchor="w")
        
        # Marco para la animación de escaneo ultra moderna
        self.scan_frame = tk.Frame(content_container, bg="#ffffff", height=120)
        self.scan_frame.pack(fill="x", pady=(0, 20))
        self.scan_frame.pack_propagate(False)
        
        # Canvas para la animación de escaneo
        self.scan_canvas = tk.Canvas(
            self.scan_frame, height=120, bg="#ffffff", highlightthickness=0
        )
        self.scan_canvas.pack(fill="both", expand=True)
        
        # Texto de estado de escaneo con contador
        self.scan_text = tk.Label(
            self.scan_frame,
            text="Esperando productos...",
            font=self.text_font,
            bg="#ffffff",
            fg="#3498db"
        )
        self.scan_text.place(relx=0.5, rely=0.75, anchor="center")
        
        # Contador de productos escaneados
        self.scan_counter = tk.Label(
            self.scan_frame,
            text="0",
            font=tkfont.Font(family="Segoe UI", size=28, weight="bold"),
            bg="#ffffff",
            fg="#2c3e50"
        )
        self.scan_counter.place(relx=0.5, rely=0.35, anchor="center")
        
        # Etiqueta del contador
        tk.Label(
            self.scan_frame,
            text="Productos escaneados",
            font=self.small_font,
            bg="#ffffff",
            fg="#7f8c8d"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Título de la sección de productos
        section_title = tk.Label(
            content_container,
            text="📋 Lista de Productos",
            font=self.subtitle_font,
            bg="#ffffff",
            fg="#2c3e50"
        )
        section_title.pack(anchor="w", pady=(0, 15))
        
        # Tabla de productos con estilo premium
        table_frame = tk.Frame(content_container, bg="#ffffff")
        table_frame.pack(fill="both", expand=True)
        
        # Crear borde redondeado simulado
        border_canvas = tk.Canvas(table_frame, bg="#ffffff", highlightthickness=0, height=2)
        border_canvas.pack(fill="x")
        border_canvas.create_rectangle(0, 0, 1000, 2, fill="#e1e8ed", outline="")

        # Columnas de la tabla (ORIGINAL: solo name y quantity)
        columns = ("name", "quantity")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=8, style="Modern.Treeview"
        )

        # Configurar encabezados con iconos (ORIGINAL)
        self.tree.heading("name", text="🛍️ Nombre del producto")
        self.tree.heading("quantity", text="📦 Cantidad")

        # Configurar anchos de columna (ORIGINAL)
        self.tree.column("name", width=300)
        self.tree.column("quantity", width=100, anchor=tk.CENTER)

        # Scrollbar para la tabla
        table_scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview, style="Modern.Vertical.TScrollbar"
        )
        self.tree.configure(yscrollcommand=table_scrollbar.set)

        # Empaquetar tabla y scrollbar
        self.tree.pack(side=tk.LEFT, fill="both", expand=True, pady=10)
        table_scrollbar.pack(side=tk.RIGHT, fill="y")
        
        # Estadísticas de escaneo
        stats_frame = tk.Frame(content_container, bg="#f8f9fa", padx=20, pady=15)
        stats_frame.pack(fill="x", pady=20)
        
        # Crear tres columnas para estadísticas
        for i, (icon, title, value) in enumerate([
            ("⏱️", "Tiempo de escaneo", "00:00"),
            ("🔄", "Último escaneo", "Esperando..."),
            ("📊", "Productos únicos", "0")
        ]):
            stat_box = tk.Frame(stats_frame, bg="#ffffff", padx=15, pady=10)
            stat_box.grid(row=0, column=i, padx=5, sticky="nsew")
            
            # Borde para la caja de estadísticas
            stat_box.config(highlightbackground="#e0e0e0", highlightthickness=1)
            
            tk.Label(
                stat_box,
                text=f"{icon} {title}",
                font=self.small_font,
                bg="#ffffff",
                fg="#7f8c8d"
            ).pack(anchor="w")
            
            # Valor dinámico que actualizaremos
            if i == 0:
                self.scan_time_label = tk.Label(
                    stat_box,
                    text=value,
                    font=tkfont.Font(family="Segoe UI", size=16, weight="bold"),
                    bg="#ffffff",
                    fg="#2c3e50"
                )
                self.scan_time_label.pack(anchor="w", pady=(5, 0))
            elif i == 1:
                self.last_scan_label = tk.Label(
                    stat_box,
                    text=value,
                    font=tkfont.Font(family="Segoe UI", size=16, weight="bold"),
                    bg="#ffffff",
                    fg="#2c3e50"
                )
                self.last_scan_label.pack(anchor="w", pady=(5, 0))
            else:
                self.unique_products_label = tk.Label(
                    stat_box,
                    text=value,
                    font=tkfont.Font(family="Segoe UI", size=16, weight="bold"),
                    bg="#ffffff",
                    fg="#2c3e50"
                )
                self.unique_products_label.pack(anchor="w", pady=(5, 0))
        
        # Configurar grid para que las columnas se expandan por igual
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)

        # Botones con diseño ultra moderno
        btn_container = tk.Frame(main_container, bg="#ffffff")
        btn_container.pack(fill="x", padx=20, pady=(20, 30))
        
        # Frame para centrar botones
        btn_frame = tk.Frame(btn_container, bg="#ffffff")
        btn_frame.pack(anchor="center")
        
        # Botón de aceptar compra con gradiente
        accept_btn = self.create_modern_button(
            btn_frame, 
            text="✅ Aceptar Compra", 
            bg_color="#27ae60",
            hover_color="#2ecc71",
            command=self.finalize_purchase
        )
        accept_btn.grid(row=0, column=0, padx=12, pady=5)
        
        # Botón de cancelar
        cancel_btn = self.create_modern_button(
            btn_frame, 
            text="❌ Cancelar", 
            bg_color="#e74c3c",
            hover_color="#ec7063",
            command=self.cancel_purchase
        )
        cancel_btn.grid(row=0, column=1, padx=12, pady=5)
        
        # Iniciar temporizador
        self.update_scan_time()
        
        # Actualizar estadísticas iniciales
        self.update_statistics()

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

    def draw_scan_icon(self, canvas):
        """Dibuja un icono de escaneo"""
        # Dibujar base del escáner
        canvas.create_rectangle(5, 25, 35, 35, fill="#ecf0f1", outline="")
        
        # Dibujar parte superior del escáner
        canvas.create_rectangle(10, 10, 30, 25, fill="#ecf0f1", outline="")
        
        # Dibujar línea de escaneo
        canvas.create_line(10, 18, 30, 18, fill="#3498db", width=2)

    def draw_avatar(self, canvas):
        """Dibuja un avatar simple"""
        canvas.create_oval(5, 5, 30, 30, fill="#3498db", outline="#2980b9", width=2)
        canvas.create_oval(12, 12, 23, 20, fill="#ffffff")
        canvas.create_arc(10, 18, 25, 30, start=0, extent=180, fill="#ffffff")

    def configure_scrollable_frame(self, event):
        """Ajusta el ancho del scrollable_frame al ancho del canvas"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

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

    def scanning_animation(self):
        """Crea una animación de escaneo ultra moderna"""
        if not self.scan_active:
            return

        try:
            self.scan_canvas.delete("scan_animation")
            
            # Obtener dimensiones
            canvas_width = self.scan_canvas.winfo_width()
            canvas_height = self.scan_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                # Dibujar círculo central
                center_x = canvas_width / 2
                center_y = canvas_height / 3
                radius = 30 + math.sin(time.time() * 2) * 3
                
                # Círculo pulsante
                self.scan_canvas.create_oval(
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius,
                    fill="#ebf5fb", outline="#3498db", width=2,
                    tags="scan_animation"
                )
                
                # Ondas de escaneo
                for i in range(3):
                    wave_radius = 10 + i * 15 + self.scan_pulse * 15
                    opacity = int(255 * (1 - self.scan_pulse))
                    if opacity < 0:
                        opacity = 0
                    color = f"#{opacity:02x}{opacity:02x}{opacity+50:02x}"
                    
                    self.scan_canvas.create_oval(
                        center_x - wave_radius, center_y - wave_radius,
                        center_x + wave_radius, center_y + wave_radius,
                        outline=color, width=1.5,
                        tags="scan_animation"
                    )
                
                # Actualizar efecto de pulso
                self.scan_pulse += 0.02
                if self.scan_pulse > 1:
                    self.scan_pulse = 0
                
                # Líneas de escaneo
                for i in range(4):
                    angle = (time.time() * 1.5 + i * math.pi / 2) % (2 * math.pi)
                    length = 60
                    end_x = center_x + math.cos(angle) * length
                    end_y = center_y + math.sin(angle) * length
                    
                    self.scan_canvas.create_line(
                        center_x, center_y, end_x, end_y,
                        fill="#3498db", width=1.5,
                        tags="scan_animation"
                    )
                
                # Efecto de escaneo horizontal
                scan_y = 20 + self.scan_effect_pos * (canvas_height - 40)
                self.scan_canvas.create_line(
                    20, scan_y, canvas_width - 20, scan_y,
                    fill="#3498db", width=2,
                    tags="scan_animation"
                )
                
                # Actualizar posición del efecto de escaneo
                self.scan_effect_pos += 0.02 * self.scan_effect_dir
                if self.scan_effect_pos > 1 or self.scan_effect_pos < 0:
                    self.scan_effect_dir *= -1
        except tk.TclError:
            pass

        # Continuar animación
        self.after(50, self.scanning_animation)

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

    def update_scan_time(self):
        """Actualiza el tiempo de escaneo"""
        if not self.scan_timer_active:
            return
        
        try:
            # Calcular tiempo transcurrido desde el inicio del escaneo
            elapsed = int(time.time() - self.scan_start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            
            # Actualizar etiqueta
            self.scan_time_label.config(text=f"{minutes:02d}:{seconds:02d}")
        except (tk.TclError, AttributeError):
            pass
        
        # Continuar actualizando cada segundo
        if self.scan_timer_active:
            self.after(1000, self.update_scan_time)

    def update_statistics(self):
        """Actualiza las estadísticas de escaneo"""
        if not self.scan_active:
            return
        
        try:
            # Obtener productos actuales
            products = self.product_viewmodel.get_products()
            
            # Calcular estadísticas
            total_items = sum(p['quantity'] for p in products) if products else 0
            unique_products = len(products)
            
            # Actualizar contador de productos escaneados
            self.scan_counter.config(text=str(total_items))
            
            # Actualizar productos únicos
            self.unique_products_label.config(text=str(unique_products))
            
            # Actualizar estado de escaneo
            if total_items == 0:
                self.scan_text.config(text="Esperando productos...")
            else:
                self.scan_text.config(text="Escaneo en progreso...")
            
        except (tk.TclError, AttributeError):
            pass
        
        # Continuar actualizando cada 500ms
        if self.scan_active:
            self.after(500, self.update_statistics)

    def start_scan_thread(self):
        """Inicia el hilo de escaneo continuo"""
        self.scan_active = True
        self.scan_timer_active = True
        self.animation_running = True
        
        # Reiniciar tiempo de escaneo
        self.scan_start_time = time.time()
        
        # Iniciar hilo de escaneo
        self.scan_thread = threading.Thread(
            target=self.scan_products_continuously, daemon=True
        )
        self.scan_thread.start()

    def scan_products_continuously(self):
        """Hilo secundario que escanea productos continuamente"""
        while self.scan_active:
            try:
                with self.scan_lock:
                    status, product = self.product_viewmodel.scan_product()
                    # Enviar feedback al proceso GPIO según resultado
                    if status == ProductScanStatus.SUCCESS and product:
                        send_gpio_feedback("SUCCESS")
                        self.scan_count += 1
                        self.after(0, self.update_table)
                        self.after(0, self.product_scanned)
                    elif status in (ProductScanStatus.ERROR, ProductScanStatus.INVALID_NAME, ProductScanStatus.DUPLICATE):
                        send_gpio_feedback("FAILURE")
                        if status == ProductScanStatus.DUPLICATE:
                            self.after(0, lambda: messagebox.showwarning("Producto duplicado", "El producto ya fue escaneado anteriormente."))
            except Exception as e:
                self.after(
                    0, lambda: messagebox.showerror("Error", f"Error al escanear: {e}")
                )

            time.sleep(0.5)

    def product_scanned(self):
        """Actualiza la interfaz cuando se escanea un producto"""
        try:
            # Obtener productos actuales
            products = self.product_viewmodel.get_products()
        
            if products:
                # Actualizar etiqueta de último escaneo
                last_product = products[-1]["name"]
                display_name = last_product[:15] + "..." if len(last_product) > 15 else last_product
                self.last_scan_label.config(text=display_name)
                
                # Efecto de pulso en el contador
                self.scan_counter.config(fg="#27ae60")
                self.after(300, lambda: self.scan_counter.config(fg="#2c3e50"))
                
                # Reiniciar animación de pulso
                self.scan_pulse = 0
                
                # Forzar actualización inmediata de estadísticas
                self.update_statistics()
            
        except (tk.TclError, AttributeError, IndexError):
            pass

    def update_table(self):
        """Actualiza la tabla de productos (LÓGICA ORIGINAL)"""
        self.tree.delete(*self.tree.get_children())
        for i, p in enumerate(self.product_viewmodel.get_products()):
            name = p["name"]
            quantity = p["quantity"]
            
            # Alternar colores de fila para mejor legibilidad
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=(name, quantity), tags=(tag,))
            
        # Configurar colores alternos
        self.tree.tag_configure("even", background="#ffffff")
        self.tree.tag_configure("odd", background="#f8f9fa")

    def stop_scan_thread(self):
        """Detiene el hilo de escaneo y todas las animaciones"""
        self.scan_active = False
        self.scan_timer_active = False
        self.animation_running = False
        
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=1)

    def finalize_purchase(self):
        """Finaliza la compra y detiene el escaneo (LÓGICA ORIGINAL)"""
        self.stop_scan_thread()
        
        # Detener todas las animaciones y timers
        self.scan_timer_active = False
        self.animation_running = False

        if not self.product_viewmodel.get_products():
            messagebox.showwarning(
                "Sin productos", "Debe escanear al menos un producto."
            )
            self.start_scan_thread()
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
            self.start_scan_thread()

    def cancel_purchase(self):
        """Cancela la compra (LÓGICA CORREGIDA)"""
        confirm = messagebox.askyesno(
            "Confirmar cancelación", "¿Estás seguro de cancelar la compra?"
        )
        if not confirm:
            return

        print("[INFO] Compra cancelada.")
        self.stop_scan_thread()
        
        # Detener todas las animaciones y timers
        self.scan_timer_active = False
        self.animation_running = False

        if self.order and "id" in self.order:
            try:
                success = self.product_viewmodel.cancel_order(self.order["id"])
                if success:
                    print("Orden cancelada exitosamente en el servidor")
                else:
                    print("Error al cancelar la orden en el servidor")
            except Exception as e:
                print(f"Error al cancelar orden: {e}")

        try:
            self.master.show_screen(
                PurchaseResultScreen,
                success=False,
                message="La compra ha sido cancelada exitosamente",
                user_data=self.user_data,
                on_return=self.on_logout,
            )
        except Exception as e:
            print(f"Error al mostrar pantalla de resultado: {e}")
            self.on_logout()

    def destroy(self):
        """Limpieza completa al cerrar la pantalla"""
        # Detener todos los procesos
        self.scan_active = False
        self.scan_timer_active = False
        self.animation_running = False
        
        # Detener hilo de escaneo
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=1)
        
        # Limpiar canvas
        try:
            self.scan_canvas.delete("all")
            self.bg_canvas.delete("all")
        except (tk.TclError, AttributeError):
            pass
        
        # Llamar al destructor padre
        super().destroy()
