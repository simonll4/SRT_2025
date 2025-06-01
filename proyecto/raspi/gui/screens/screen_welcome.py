import tkinter as tk
from tkinter import font as tkfont
import math
import random
import time


class WelcomeScreen(tk.Frame):
    def __init__(self, master, on_start_purchase, on_logout, user_data, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.configure(bg="#f8f9fa")
        self.on_start_purchase = on_start_purchase
        self.on_logout = on_logout
        self.user_data = user_data
        
        # Variables para animaciones
        self.animation_running = True
        self.welcome_pulse = 0
        self.balance_glow = 0
        self.coin_rotation = 0
        self.sparkles = []
        self.floating_money = []
        self.wave_offset = 0
        self.card_hover = 0
        
        # Crear fuentes personalizadas más elegantes
        self.title_font = tkfont.Font(family="Segoe UI", size=32, weight="bold")
        self.welcome_font = tkfont.Font(family="Segoe UI", size=28, weight="bold")
        self.subtitle_font = tkfont.Font(family="Segoe UI", size=20, weight="normal")
        self.text_font = tkfont.Font(family="Segoe UI", size=16, weight="normal")
        self.balance_font = tkfont.Font(family="Segoe UI", size=32, weight="bold")
        self.small_font = tkfont.Font(family="Segoe UI", size=12, weight="normal")
        
        self.create_widgets()
        
        # Iniciar animaciones
        self.after(100, self.animate_background)
        self.after(200, self.animate_welcome_effects)
        self.after(300, self.animate_balance_card)

    def create_widgets(self):
        # Canvas principal para efectos de fondo
        self.bg_canvas = tk.Canvas(self, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Contenedor principal con efecto de tarjeta premium
        main_container = tk.Frame(self, bg="#ffffff")
        main_container.place(relx=0.5, rely=0.5, anchor="center", 
                            relwidth=0.9, relheight=0.9)
        
        # Crear múltiples sombras para efecto de profundidad
        for i in range(5):
            shadow_intensity = 220 - i * 15
            shadow_color = f"#{shadow_intensity:02x}{shadow_intensity:02x}{shadow_intensity:02x}"
            shadow = tk.Frame(self, bg=shadow_color)
            shadow.place(relx=0.5, rely=0.5, anchor="center", 
                        relwidth=0.9 + i*0.01, relheight=0.9 + i*0.01)
        
        main_container.lift()
        
        # Encabezado con gradiente espectacular
        header_frame = tk.Frame(main_container, bg="#2c3e50", height=140)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Canvas para el encabezado con efectos
        self.header_canvas = tk.Canvas(header_frame, height=140, bg="#2c3e50", 
                                      highlightthickness=0)
        self.header_canvas.pack(fill="both", expand=True)
        
        # Crear gradiente animado en el encabezado
        self.animate_header_gradient()
        
        # Contenido principal
        content_frame = tk.Frame(main_container, bg="#ffffff", padx=40, pady=30)
        content_frame.pack(fill="both", expand=True)
        
        # Mensaje de bienvenida con efectos
        welcome_container = tk.Frame(content_frame, bg="#ffffff")
        welcome_container.pack(fill="x", pady=(0, 30))
        
        # Canvas para efectos de bienvenida
        self.welcome_canvas = tk.Canvas(welcome_container, height=80, bg="#ffffff", 
                                       highlightthickness=0)
        self.welcome_canvas.pack(fill="x")
        
        # Información del usuario con diseño de tarjeta premium
        user_section = tk.Frame(content_frame, bg="#ffffff")
        user_section.pack(fill="x", pady=(0, 40))
        
        # Tarjeta de información del usuario
        self.user_card = tk.Frame(user_section, bg="#f8fbff", padx=35, pady=30)
        self.user_card.pack(fill="x")
        
        # Borde elegante para la tarjeta
        self.user_card.config(relief="solid", bd=1, highlightbackground="#e1e8ed", highlightthickness=2)
        
        # Canvas para línea decorativa superior
        user_decoration = tk.Canvas(self.user_card, height=4, bg="#f8fbff", highlightthickness=0)
        user_decoration.pack(fill="x", pady=(0, 20))
        self.create_decorative_line(user_decoration, "#3498db")
        
        # Información del usuario
        user_info_frame = tk.Frame(self.user_card, bg="#f8fbff")
        user_info_frame.pack(fill="x")
        
        # Avatar y nombre
        user_header = tk.Frame(user_info_frame, bg="#f8fbff")
        user_header.pack(fill="x", pady=(0, 20))
        
        # Canvas para avatar animado
        self.avatar_canvas = tk.Canvas(user_header, width=60, height=60, 
                                      bg="#f8fbff", highlightthickness=0)
        self.avatar_canvas.pack(side=tk.LEFT, padx=(0, 20))
        
        # Información del usuario
        user_text_frame = tk.Frame(user_header, bg="#f8fbff")
        user_text_frame.pack(side=tk.LEFT, fill="both", expand=True)
        
        nombre = self.user_data.get("nombre", "Usuario")
        
        # Saludo personalizado
        greeting_label = tk.Label(
            user_text_frame, 
            text=f"¡Bienvenido/a, {nombre}!",
            font=self.welcome_font,
            bg="#f8fbff",
            fg="#2c3e50"
        )
        greeting_label.pack(anchor="w")
        
        # Mensaje adicional
        message_label = tk.Label(
            user_text_frame,
            text="Estamos listos para tu experiencia de compra",
            font=self.text_font,
            bg="#f8fbff",
            fg="#7f8c8d"
        )
        message_label.pack(anchor="w", pady=(5, 0))
        
        # Separador elegante
        separator_frame = tk.Frame(self.user_card, bg="#f8fbff", height=20)
        separator_frame.pack(fill="x")
        separator_frame.pack_propagate(False)
        
        separator_canvas = tk.Canvas(separator_frame, height=2, bg="#f8fbff", highlightthickness=0)
        separator_canvas.pack(fill="x", pady=10)
        self.create_decorative_line(separator_canvas, "#bdc3c7")
        
        # Sección de saldo con efectos espectaculares
        balance_section = tk.Frame(self.user_card, bg="#f8fbff")
        balance_section.pack(fill="x")
        
        # Canvas para efectos de saldo
        self.balance_canvas = tk.Canvas(balance_section, height=120, bg="#f8fbff", 
                                       highlightthickness=0)
        self.balance_canvas.pack(fill="x")
        
        # Botones con diseño ultra moderno
        btn_container = tk.Frame(content_frame, bg="#ffffff")
        btn_container.pack(fill="x", pady=(20, 0))
        
        # Frame para centrar botones
        btn_frame = tk.Frame(btn_container, bg="#ffffff")
        btn_frame.pack(anchor="center")
        
        # Botón de compra con efectos
        self.start_btn = self.create_modern_button(
            btn_frame, 
            text="🛒 Empezar Compra", 
            bg_color="#27ae60",
            hover_color="#2ecc71",
            command=self.on_start_purchase,
            icon="🛒"
        )
        self.start_btn.grid(row=0, column=0, padx=20, pady=5)
        
        # Botón de salida
        self.exit_btn = self.create_modern_button(
            btn_frame, 
            text="🚪 Salir", 
            bg_color="#e74c3c",
            hover_color="#ec7063",
            command=self.on_logout,
            icon="🚪"
        )
        self.exit_btn.grid(row=0, column=1, padx=20, pady=5)
        
        # Pie de página con diseño elegante
        footer_frame = tk.Frame(main_container, bg="#f8f9fa", height=50)
        footer_frame.pack(side=tk.BOTTOM, fill="x")
        footer_frame.pack_propagate(False)
        
        # Canvas para línea decorativa en el footer
        footer_canvas = tk.Canvas(footer_frame, height=2, bg="#f8f9fa", highlightthickness=0)
        footer_canvas.pack(fill="x", pady=(10, 5))
        self.create_decorative_line(footer_canvas, "#3498db")
        
        footer_label = tk.Label(
            footer_frame,
            text="🏪 Sistema de Autocashier v2.0 • Tecnología de vanguardia para tu comodidad",
            font=self.small_font,
            bg="#f8f9fa",
            fg="#95a5a6"
        )
        footer_label.pack()
        
        # Inicializar animaciones específicas
        self.animate_avatar()

    def create_modern_button(self, parent, text, bg_color, hover_color, command, icon=""):
        """Crea un botón moderno con efectos hover y animaciones"""
        btn = tk.Button(
            parent,
            text=text,
            font=tkfont.Font(family="Segoe UI", size=16, weight="bold"),
            bg=bg_color,
            fg="#ffffff",
            activebackground=hover_color,
            activeforeground="#ffffff",
            padx=30,
            pady=15,
            border=0,
            cursor="hand2",
            command=command,
            relief="flat"
        )
        
        # Efectos hover con animación
        def on_enter(e):
            btn.config(bg=hover_color)
            # Efecto de escala simulado con padding
            btn.config(padx=35, pady=18)
        
        def on_leave(e):
            btn.config(bg=bg_color)
            btn.config(padx=30, pady=15)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

    def create_decorative_line(self, canvas, color):
        """Crea una línea decorativa con gradiente"""
        canvas.update_idletasks()
        width = canvas.winfo_width()
        
        if width > 1:
            for i in range(width):
                alpha = math.sin(math.pi * i / width)
                r, g, b = self.hex_to_rgb(color)
                r = int(r + (255 - r) * (1 - alpha))
                g = int(g + (255 - g) * (1 - alpha))
                b = int(b + (255 - b) * (1 - alpha))
                line_color = f"#{r:02x}{g:02x}{b:02x}"
                canvas.create_line(i, 1, i, 2, fill=line_color)

    def hex_to_rgb(self, hex_color):
        """Convierte color hex a RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def animate_background(self):
        """Anima el fondo con efectos de dinero flotante"""
        if not self.animation_running:
            return
            
        try:
            self.bg_canvas.delete("bg_effects")
            
            width = self.bg_canvas.winfo_width()
            height = self.bg_canvas.winfo_height()
            
            if width > 1 and height > 1:
                time_offset = time.time() * 0.4
                
                # Ondas de fondo sutiles
                for i in range(6):
                    wave_y = height * (0.15 + 0.15 * i) + 25 * math.sin(time_offset + i)
                    wave_amplitude = 20 + 8 * math.sin(time_offset * 0.8 + i)
                    
                    points = []
                    for x in range(0, width + 15, 15):
                        y = wave_y + wave_amplitude * math.sin((x / 60) + time_offset + i)
                        points.extend([x, y])
                    
                    if len(points) >= 4:
                        alpha = int(15 + 10 * math.sin(time_offset + i))
                        color = f"#{alpha:02x}{alpha+20:02x}{alpha+40:02x}"
                        
                        self.bg_canvas.create_line(
                            points, fill=color, width=1, smooth=True,
                            tags="bg_effects"
                        )
                
                # Símbolos de dinero flotantes
                money_symbols = ["💰", "💵", "💳", "🪙", "💎", "✨"]
                
                # Actualizar partículas de dinero flotante
                if len(self.floating_money) < 12:
                    for _ in range(2):
                        self.floating_money.append({
                            'x': random.randint(0, width),
                            'y': height + 20,
                            'vx': random.uniform(-1, 1),
                            'vy': random.uniform(-3, -1),
                            'symbol': random.choice(money_symbols),
                            'size': random.randint(12, 20),
                            'rotation': random.uniform(0, 360),
                            'alpha': random.uniform(0.3, 0.8)
                        })
                
                # Animar partículas de dinero
                for particle in self.floating_money[:]:
                    particle['x'] += particle['vx']
                    particle['y'] += particle['vy']
                    particle['rotation'] += 2
                    
                    if particle['y'] < -30:
                        self.floating_money.remove(particle)
                        continue
                    
                    # Dibujar símbolo de dinero
                    alpha = int(255 * particle['alpha'])
                    color = f"#{alpha:02x}{alpha+50:02x}{alpha:02x}"
                    
                    self.bg_canvas.create_text(
                        particle['x'], particle['y'], 
                        text=particle['symbol'],
                        font=("Arial", particle['size']), 
                        fill=color, tags="bg_effects"
                    )
                
                # Partículas de brillo
                for i in range(20):
                    x = (i * width / 20 + math.sin(time_offset * 2 + i) * 30) % width
                    y = (math.sin(time_offset * 1.5 + i * 0.3) * height * 0.4 + height * 0.5) % height
                    size = 1 + math.sin(time_offset * 3 + i)
                    
                    alpha = int(50 + 30 * math.sin(time_offset * 2 + i))
                    color = f"#{alpha+100:02x}{alpha+150:02x}{alpha:02x}"
                    
                    self.bg_canvas.create_oval(
                        x - size, y - size, x + size, y + size,
                        fill=color, outline="", tags="bg_effects"
                    )
            
            self.after(80, self.animate_background)
        except tk.TclError:
            pass

    def animate_header_gradient(self):
        """Anima el gradiente del encabezado"""
        if not self.animation_running:
            return
            
        try:
            self.header_canvas.delete("header_effects")
            
            width = self.header_canvas.winfo_width()
            height = self.header_canvas.winfo_height()
            
            if width > 1 and height > 1:
                time_offset = time.time() * 0.5
                
                # Gradiente animado
                for i in range(height):
                    ratio = i / height
                    wave = 0.1 * math.sin(time_offset + ratio * 4)
                    
                    r = int(44 + wave * 20)
                    g = int(62 + wave * 30)
                    b = int(80 + wave * 40)
                    
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    self.header_canvas.create_line(0, i, width, i, fill=color, tags="header_effects")
                
                # Logo animado
                logo_x, logo_y = 80, 70
                logo_scale = 1.0 + 0.1 * math.sin(time_offset * 2)
                logo_radius = int(35 * logo_scale)
                
                # Aura del logo
                aura_radius = logo_radius + 8 + 3 * math.sin(time_offset * 4)
                alpha = int(100 + 50 * math.sin(time_offset * 3))
                aura_color = f"#{alpha:02x}{alpha:02x}{255:02x}"
                
                self.header_canvas.create_oval(
                    logo_x - aura_radius, logo_y - aura_radius,
                    logo_x + aura_radius, logo_y + aura_radius,
                    fill=aura_color, outline="", tags="header_effects"
                )
                
                # Logo principal
                self.header_canvas.create_oval(
                    logo_x - logo_radius, logo_y - logo_radius,
                    logo_x + logo_radius, logo_y + logo_radius,
                    fill="#ffffff", outline="#ecf0f1", width=2, tags="header_effects"
                )
                
                # Texto del logo
                self.header_canvas.create_text(
                    logo_x, logo_y, text="AC", 
                    font=tkfont.Font(family="Segoe UI", size=int(24 * logo_scale), weight="bold"), 
                    fill="#3498db", tags="header_effects"
                )
                
                # Título principal
                title_x = 200
                title_glow = int(200 + 55 * math.sin(time_offset * 2))
                title_color = f"#{title_glow:02x}{title_glow:02x}{255:02x}"
                
                self.header_canvas.create_text(
                    title_x, logo_y, text="AUTOCASHIER", 
                    font=self.title_font, fill=title_color, anchor="w", tags="header_effects"
                )
                
                # Subtítulo
                self.header_canvas.create_text(
                    title_x, logo_y + 25, text="Sistema Inteligente de Compras", 
                    font=tkfont.Font(family="Segoe UI", size=14), 
                    fill="#bdc3c7", anchor="w", tags="header_effects"
                )
                
                # Partículas decorativas en el header
                for i in range(8):
                    particle_angle = (time_offset * 30 + i * 45) * math.pi / 180
                    particle_radius = 100 + 20 * math.sin(time_offset + i)
                    particle_x = logo_x + math.cos(particle_angle) * particle_radius
                    particle_y = logo_y + math.sin(particle_angle) * particle_radius
                    
                    if 0 <= particle_x <= width and 0 <= particle_y <= height:
                        size = 1 + math.sin(time_offset * 3 + i)
                        alpha = int(100 + 50 * math.sin(time_offset * 2 + i))
                        color = f"#{alpha:02x}{alpha:02x}{255:02x}"
                        
                        self.header_canvas.create_oval(
                            particle_x - size, particle_y - size,
                            particle_x + size, particle_y + size,
                            fill=color, outline="", tags="header_effects"
                        )
            
            self.after(60, self.animate_header_gradient)
        except tk.TclError:
            pass

    def animate_welcome_effects(self):
        """Anima los efectos de bienvenida"""
        if not self.animation_running:
            return
            
        try:
            self.welcome_canvas.delete("all")
            
            width = self.welcome_canvas.winfo_width()
            height = self.welcome_canvas.winfo_height()
            
            if width > 1 and height > 1:
                time_offset = time.time()
                
                # Texto de bienvenida con efectos
                center_x = width / 2
                center_y = height / 2
                
                # Aura del texto
                self.welcome_pulse = (math.sin(time_offset * 3) + 1) / 2
                aura_size = 5 + 3 * self.welcome_pulse
                alpha = int(50 + 30 * self.welcome_pulse)
                aura_color = f"#{alpha:02x}{alpha+50:02x}{alpha:02x}"
                
                # Crear múltiples capas de texto para efecto de brillo
                for i in range(3):
                    offset = i * 2
                    text_alpha = int(255 - i * 50)
                    text_color = f"#{text_alpha:02x}{text_alpha:02x}{text_alpha:02x}"
                    
                    self.welcome_canvas.create_text(
                        center_x + offset, center_y + offset, 
                        text="¡Tu experiencia de compra comienza aquí!",
                        font=tkfont.Font(family="Segoe UI", size=18, weight="bold"),
                        fill=text_color, anchor="center"
                    )
                
                # Texto principal
                self.welcome_canvas.create_text(
                    center_x, center_y, 
                    text="¡Tu experiencia de compra comienza aquí!",
                    font=tkfont.Font(family="Segoe UI", size=18, weight="bold"),
                    fill="#2c3e50", anchor="center"
                )
                
                # Estrellas decorativas
                for i in range(6):
                    star_angle = (time_offset * 50 + i * 60) * math.pi / 180
                    star_radius = 150 + 30 * math.sin(time_offset + i)
                    star_x = center_x + math.cos(star_angle) * star_radius
                    star_y = center_y + math.sin(star_angle) * star_radius
                    
                    if 0 <= star_x <= width and 0 <= star_y <= height:
                        star_size = 8 + 4 * math.sin(time_offset * 2 + i)
                        self.welcome_canvas.create_text(
                            star_x, star_y, text="✨",
                            font=("Arial", int(star_size)), fill="#f1c40f"
                        )
            
            self.after(70, self.animate_welcome_effects)
        except tk.TclError:
            pass

    def animate_avatar(self):
        """Anima el avatar del usuario"""
        if not self.animation_running:
            return
            
        try:
            self.avatar_canvas.delete("all")
            
            center_x, center_y = 30, 30
            time_offset = time.time()
            
            # Escala pulsante
            scale = 1.0 + 0.1 * math.sin(time_offset * 2)
            radius = int(25 * scale)
            
            # Aura del avatar
            aura_radius = radius + 5 + 3 * math.sin(time_offset * 4)
            alpha = int(100 + 50 * math.sin(time_offset * 3))
            aura_color = f"#{alpha:02x}{alpha:02x}{alpha+100:02x}"
            
            self.avatar_canvas.create_oval(
                center_x - aura_radius, center_y - aura_radius,
                center_x + aura_radius, center_y + aura_radius,
                fill=aura_color, outline=""
            )
            
            # Avatar principal
            self.avatar_canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill="#3498db", outline="#2980b9", width=2
            )
            
            # Cara del avatar
            eye_size = int(3 * scale)
            self.avatar_canvas.create_oval(
                center_x - 8, center_y - 5, center_x - 4, center_y - 1,
                fill="#ffffff"
            )
            self.avatar_canvas.create_oval(
                center_x + 4, center_y - 5, center_x + 8, center_y - 1,
                fill="#ffffff"
            )
            
            # Sonrisa
            smile_width = int(12 * scale)
            self.avatar_canvas.create_arc(
                center_x - smile_width//2, center_y + 2,
                center_x + smile_width//2, center_y + 12,
                start=0, extent=180, style=tk.ARC,
                outline="#ffffff", width=2
            )
            
            self.after(50, self.animate_avatar)
        except tk.TclError:
            pass

    def animate_balance_card(self):
        """Anima la tarjeta de saldo con efectos espectaculares"""
        if not self.animation_running:
            return
            
        try:
            self.balance_canvas.delete("all")
            
            width = self.balance_canvas.winfo_width()
            height = self.balance_canvas.winfo_height()
            
            if width > 1 and height > 1:
                time_offset = time.time()
                center_x = width / 2
                center_y = height / 2
                
                # Efectos de fondo para el saldo
                for i in range(4):
                    ring_radius = 40 + i * 15 + 8 * math.sin(time_offset * 2 + i)
                    alpha = int(80 - i * 15 + 30 * math.sin(time_offset * 3 + i))
                    if alpha > 0:
                        color = f"#{alpha:02x}{alpha+100:02x}{alpha:02x}"
                        self.balance_canvas.create_oval(
                            center_x - ring_radius, center_y - ring_radius,
                            center_x + ring_radius, center_y + ring_radius,
                            outline=color, width=1
                        )
                
                # Ícono de moneda animado
                coin_x = 80
                self.coin_rotation += 3
                coin_scale = 1.0 + 0.15 * math.sin(time_offset * 2)
                coin_radius = int(25 * coin_scale)
                
                # Sombra de la moneda
                shadow_offset = 3
                self.balance_canvas.create_oval(
                    coin_x - coin_radius + shadow_offset, center_y - coin_radius + shadow_offset,
                    coin_x + coin_radius + shadow_offset, center_y + coin_radius + shadow_offset,
                    fill="#d5d8dc", outline=""
                )
                
                # Moneda principal
                self.balance_canvas.create_oval(
                    coin_x - coin_radius, center_y - coin_radius,
                    coin_x + coin_radius, center_y + coin_radius,
                    fill="#f1c40f", outline="#f39c12", width=3
                )
                
                # Símbolo de dinero en la moneda
                self.balance_canvas.create_text(
                    coin_x, center_y, text="$",
                    font=tkfont.Font(family="Segoe UI", size=int(20 * coin_scale), weight="bold"),
                    fill="#ffffff"
                )
                
                # Brillo en la moneda
                highlight_size = int(8 * coin_scale)
                self.balance_canvas.create_oval(
                    coin_x - highlight_size, center_y - highlight_size,
                    coin_x, center_y,
                    fill="#ffffff", outline="", stipple="gray25"
                )
                
                # Texto de saldo
                saldo = self.user_data.get("saldo", 0.0)
                
                # Etiqueta "Tu saldo actual"
                self.balance_canvas.create_text(
                    center_x, center_y - 25,
                    text="💰 Tu saldo actual:",
                    font=tkfont.Font(family="Segoe UI", size=16, weight="normal"),
                    fill="#7f8c8d", anchor="center"
                )
                
                # Valor del saldo con efectos
                self.balance_glow = (math.sin(time_offset * 2) + 1) / 2
                glow_intensity = int(39 + 50 * self.balance_glow)
                balance_color = f"#{glow_intensity:02x}{174:02x}{96:02x}"
                
                # Sombra del texto del saldo
                self.balance_canvas.create_text(
                    center_x + 2, center_y + 12,
                    text=f"${saldo:.2f}",
                    font=self.balance_font,
                    fill="#d5d8dc", anchor="center"
                )
                
                # Texto principal del saldo
                self.balance_canvas.create_text(
                    center_x, center_y + 10,
                    text=f"${saldo:.2f}",
                    font=self.balance_font,
                    fill=balance_color, anchor="center"
                )
                
                # Partículas de dinero alrededor del saldo
                for i in range(8):
                    particle_angle = (time_offset * 40 + i * 45) * math.pi / 180
                    particle_radius = 120 + 20 * math.sin(time_offset + i)
                    particle_x = center_x + math.cos(particle_angle) * particle_radius
                    particle_y = center_y + math.sin(particle_angle) * particle_radius
                    
                    if 0 <= particle_x <= width and 0 <= particle_y <= height:
                        symbols = ["💵", "💰", "🪙", "💎"]
                        symbol = symbols[i % len(symbols)]
                        size = 8 + 4 * math.sin(time_offset * 3 + i)
                        
                        self.balance_canvas.create_text(
                            particle_x, particle_y, text=symbol,
                            font=("Arial", int(size)), fill="#f1c40f"
                        )
                
                # Mensaje motivacional
                if saldo > 100:
                    message = "¡Excelente! Tienes suficiente saldo para comprar"
                    msg_color = "#27ae60"
                elif saldo > 50:
                    message = "Buen saldo disponible para tus compras"
                    msg_color = "#f39c12"
                else:
                    message = "Considera recargar tu saldo pronto"
                    msg_color = "#e74c3c"
                
                self.balance_canvas.create_text(
                    center_x, center_y + 45,
                    text=message,
                    font=tkfont.Font(family="Segoe UI", size=12, weight="normal"),
                    fill=msg_color, anchor="center"
                )
            
            self.after(60, self.animate_balance_card)
        except tk.TclError:
            pass

    def destroy(self):
        """Limpieza completa al cerrar la pantalla"""
        self.animation_running = False
        
        # Limpiar partículas
        self.floating_money.clear()
        self.sparkles.clear()
        
        # Limpiar canvas
        try:
            self.bg_canvas.delete("all")
            self.header_canvas.delete("all")
            self.welcome_canvas.delete("all")
            self.balance_canvas.delete("all")
            self.avatar_canvas.delete("all")
        except (tk.TclError, AttributeError):
            pass
        
        # Llamar al destructor padre
        super().destroy()