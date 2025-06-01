import tkinter as tk
from tkinter import ttk, font as tkfont
import threading
import time
import math
import random


class PurchaseResultScreen(tk.Frame):
    def __init__(
        self,
        master,
        success,
        message,
        user_data=None,
        on_return=None,
        *args,
        **kwargs,
    ):
        super().__init__(master, *args, **kwargs)
        self.configure(bg="#f8f9fa")
        self.master = master
        self.success = success
        self.message = message
        self.user_data = user_data
        self.on_return = on_return if on_return else lambda: None

        # Variables para animaciones
        self.animation_running = True
        self.celebration_particles = []
        self.icon_scale = 1.0
        self.icon_rotation = 0
        self.pulse_alpha = 0
        self.confetti_particles = []
        
        # Crear fuentes personalizadas más elegantes
        self.title_font = tkfont.Font(family="Segoe UI", size=36, weight="bold")
        self.subtitle_font = tkfont.Font(family="Segoe UI", size=22, weight="normal")
        self.text_font = tkfont.Font(family="Segoe UI", size=16, weight="normal")
        self.countdown_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.small_font = tkfont.Font(family="Segoe UI", size=12, weight="normal")
        
        self.pack_propagate(False)

        self.create_widgets()
        self.start_countdown()
        
        # Iniciar animaciones después de que la ventana esté lista
        self.after(100, self.animate_background)
        self.after(200, self.animate_celebration)

    def create_widgets(self):
        # Canvas principal para efectos de fondo
        self.bg_canvas = tk.Canvas(self, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Contenedor principal con efecto de tarjeta premium
        main_container = tk.Frame(self, bg="#ffffff")
        main_container.place(relx=0.5, rely=0.5, anchor="center", 
                            relwidth=0.9, relheight=0.9)
        
        # Crear efecto de sombra múltiple
        for i in range(3):
            shadow = tk.Frame(self, bg=f"#{'d' if i == 0 else 'e' if i == 1 else 'f'}0d0d0")
            shadow.place(relx=0.5, rely=0.5, anchor="center", 
                        relwidth=0.9 + i*0.005, relheight=0.9 + i*0.005)
        
        main_container.lift()
        
        # Canvas para gradiente en el contenedor principal
        gradient_canvas = tk.Canvas(main_container, highlightthickness=0)
        gradient_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Crear gradiente de fondo
        self.create_gradient_background(gradient_canvas)
        
        # Contenido principal
        content_frame = tk.Frame(main_container, bg="#ffffff")
        content_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.85)
        
        # Hacer el fondo transparente
        content_frame.configure(bg=gradient_canvas.cget('bg'))
        
        # Espacio superior con animación
        spacer_top = tk.Frame(content_frame, height=40, bg="#ffffff")
        spacer_top.pack(fill="x")
        
        # Ícono de resultado con animación espectacular
        icon_frame = tk.Frame(content_frame, bg="#ffffff", height=150)
        icon_frame.pack(fill="x")
        icon_frame.pack_propagate(False)
        
        # Canvas para el ícono animado con efectos
        self.icon_canvas = tk.Canvas(
            icon_frame, width=120, height=120,
            bg="#ffffff", highlightthickness=0
        )
        self.icon_canvas.pack()
        
        # Iniciar animación del ícono
        self.animate_icon()
        
        # Título principal con efectos
        if self.success:
            main_message = "¡Compra Exitosa!"
            title_color = "#27ae60"
            bg_color = "#ffffff"
        else:
            main_message = "Compra Cancelada"
            title_color = "#e74c3c"
            bg_color = "#ffffff"
        
        # Frame para el título con efectos
        title_frame = tk.Frame(content_frame, bg="#ffffff")
        title_frame.pack(pady=(20, 15))
        
        self.title_label = tk.Label(
            title_frame,
            text=main_message,
            font=self.title_font,
            bg="#ffffff",
            fg=title_color,
        )
        self.title_label.pack()
        
        # Mensaje secundario mejorado con iconos
        secondary_message = self.get_secondary_message()
        
        message_frame = tk.Frame(content_frame, bg="#ffffff")
        message_frame.pack(pady=(0, 30))
        
        # Icono para el mensaje
        icon_text = "✅" if self.success else "⚠️"
        tk.Label(
            message_frame,
            text=icon_text,
            font=tkfont.Font(family="Segoe UI", size=20),
            bg="#ffffff",
            fg=title_color
        ).pack()
        
        tk.Label(
            message_frame,
            text=secondary_message,
            font=self.text_font,
            bg="#ffffff",
            fg="#555555",
            wraplength=600,
            justify="center"
        ).pack(pady=(10, 0))
        
        # Información del usuario con diseño premium
        if self.user_data:
            user_container = tk.Frame(content_frame, bg="#ffffff")
            user_container.pack(pady=(0, 30), fill="x")
            
            # Crear tarjeta de usuario con gradiente
            user_card = tk.Frame(user_container, bg="#ffffff", padx=30, pady=25)
            user_card.pack(padx=40)
            
            # Borde elegante para la tarjeta
            user_card.config(relief="solid", bd=1, highlightbackground="#e1e8ed", highlightthickness=1)
            
            # Canvas para efectos en la tarjeta de usuario
            user_canvas = tk.Canvas(user_card, height=3, highlightthickness=0)
            user_canvas.pack(fill="x", pady=(0, 20))
            
            # Línea decorativa con gradiente
            self.create_decorative_line(user_canvas, title_color)
            
            # Título de la tarjeta con icono
            title_user_frame = tk.Frame(user_card, bg="#ffffff")
            title_user_frame.pack(fill="x", pady=(0, 20))
            
            tk.Label(
                title_user_frame,
                text="👤 Información del Usuario",
                font=tkfont.Font(family="Segoe UI", size=16, weight="bold"),
                bg="#ffffff",
                fg="#2c3e50"
            ).pack()
            
            # Grid para información del usuario
            info_grid = tk.Frame(user_card, bg="#ffffff")
            info_grid.pack(fill="x")
            
            # Configurar grid
            info_grid.grid_columnconfigure(1, weight=1)
            
            # Nombre del usuario
            tk.Label(
                info_grid,
                text="Nombre:",
                font=tkfont.Font(family="Segoe UI", size=13, weight="bold"),
                bg="#ffffff",
                fg="#7f8c8d",
            ).grid(row=0, column=0, sticky="w", padx=(0, 15), pady=(0, 10))
            
            name_frame = tk.Frame(info_grid, bg="#f8f9fa", padx=15, pady=8)
            name_frame.grid(row=0, column=1, sticky="ew", pady=(0, 10))
            
            tk.Label(
                name_frame,
                text=self.user_data.get('nombre', 'N/A'),
                font=tkfont.Font(family="Segoe UI", size=13),
                bg="#f8f9fa",
                fg="#2c3e50",
            ).pack(anchor="w")

            # ID del usuario
            tk.Label(
                info_grid,
                text="ID Usuario:",
                font=tkfont.Font(family="Segoe UI", size=13, weight="bold"),
                bg="#ffffff",
                fg="#7f8c8d",
            ).grid(row=1, column=0, sticky="w", padx=(0, 15))
            
            id_frame = tk.Frame(info_grid, bg="#f8f9fa", padx=15, pady=8)
            id_frame.grid(row=1, column=1, sticky="ew")
            
            user_id = self.user_data.get('external_id', 'N/A')
            tk.Label(
                id_frame,
                text=user_id,
                font=tkfont.Font(family="Segoe UI", size=12),
                bg="#f8f9fa",
                fg="#2c3e50",
                wraplength=300,
                justify="left"
            ).pack(anchor="w")
        
        # Espacio antes del contador
        spacer_mid = tk.Frame(content_frame, height=30, bg="#ffffff")
        spacer_mid.pack(fill="x")
        
        # Contador regresivo con diseño futurista
        countdown_container = tk.Frame(content_frame, bg="#ffffff")
        countdown_container.pack()
        
        countdown_frame = tk.Frame(countdown_container, bg="#ffffff", padx=25, pady=20)
        countdown_frame.pack()
        
        # Borde elegante para el contador
        countdown_frame.config(relief="solid", bd=1, highlightbackground="#e1e8ed", highlightthickness=1)
        
        # Canvas para el círculo de progreso mejorado
        self.progress_canvas = tk.Canvas(
            countdown_frame, width=80, height=80,
            bg="#ffffff", highlightthickness=0
        )
        self.progress_canvas.pack(side=tk.LEFT, padx=(0, 20))
        
        # Contenedor para texto del contador
        countdown_text_frame = tk.Frame(countdown_frame, bg="#ffffff")
        countdown_text_frame.pack(side=tk.LEFT, fill="y")
        
        # Título del contador
        tk.Label(
            countdown_text_frame,
            text="🔄 Redirección automática",
            font=tkfont.Font(family="Segoe UI", size=14, weight="bold"),
            bg="#ffffff",
            fg="#2c3e50",
        ).pack(anchor="w")
        
        # Texto del contador
        self.countdown_label = tk.Label(
            countdown_text_frame,
            text="Volviendo en 5 segundos...",
            font=self.countdown_font,
            bg="#ffffff",
            fg="#7f8c8d",
        )
        self.countdown_label.pack(anchor="w", pady=(5, 0))
        
        # Pie de página con diseño elegante
        footer_frame = tk.Frame(main_container, bg="#f8f9fa", height=50)
        footer_frame.pack(side=tk.BOTTOM, fill="x")
        footer_frame.pack_propagate(False)
        
        # Canvas para línea decorativa en el footer
        footer_canvas = tk.Canvas(footer_frame, height=2, bg="#f8f9fa", highlightthickness=0)
        footer_canvas.pack(fill="x", pady=(0, 15))
        
        self.create_decorative_line(footer_canvas, title_color)
        
        footer_label = tk.Label(
            footer_frame,
            text="✨ Gracias por usar nuestro sistema de compras ✨",
            font=tkfont.Font(family="Segoe UI", size=12, weight="normal"),
            bg="#f8f9fa",
            fg="#95a5a6",
        )
        footer_label.pack()

    def create_gradient_background(self, canvas):
        """Crea un gradiente de fondo basado en el resultado"""
        canvas.update_idletasks()
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width > 1 and height > 1:
            if self.success:
                color1, color2 = "#f8fff8", "#e8f5e8"
            else:
                color1, color2 = "#fff8f8", "#f8e8e8"
            
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

    def create_decorative_line(self, canvas, color):
        """Crea una línea decorativa con gradiente"""
        canvas.update_idletasks()
        width = canvas.winfo_width()
        
        if width > 1:
            # Línea central con gradiente
            for i in range(width):
                alpha = math.sin(math.pi * i / width)
                # Simular transparencia con colores más claros
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

    def get_secondary_message(self):
        """Genera mensajes secundarios más apropiados y elegantes"""
        if self.success:
            return "Su transacción se ha procesado correctamente.\nRecibirá un comprobante por email en breve."
        else:
            # Determinar el tipo de fallo basado en el mensaje original
            if "cancelada" in self.message.lower():
                return "La operación fue cancelada por el usuario.\nNo se realizó ningún cargo a su cuenta."
            elif "error" in self.message.lower():
                return "Se produjo un error durante el procesamiento.\nPor favor, intente nuevamente."
            else:
                return "La transacción no pudo completarse.\nVerifique sus datos e intente nuevamente."

    def animate_icon(self):
        """Anima el ícono de resultado con efectos espectaculares"""
        if not self.animation_running:
            return
            
        try:
            self.icon_canvas.delete("all")
            
            # Actualizar variables de animación
            self.icon_scale = 1.0 + 0.1 * math.sin(time.time() * 2)
            self.icon_rotation += 1
            self.pulse_alpha = (math.sin(time.time() * 3) + 1) / 2
            
            center_x, center_y = 60, 60
            base_radius = 35
            radius = base_radius * self.icon_scale
            
            if self.success:
                # Círculo verde con efectos
                # Aura externa
                aura_radius = radius + 10 + 5 * math.sin(time.time() * 4)
                alpha = int(50 + 30 * self.pulse_alpha)
                aura_color = f"#{alpha:02x}{255:02x}{alpha:02x}"
                
                self.icon_canvas.create_oval(
                    center_x - aura_radius, center_y - aura_radius,
                    center_x + aura_radius, center_y + aura_radius,
                    fill=aura_color, outline=""
                )
                
                # Círculo principal
                self.icon_canvas.create_oval(
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius,
                    fill="#27ae60", outline="#1e8449", width=3
                )
                
                # Checkmark animado con rotación
                check_size = radius * 0.6
                self.icon_canvas.create_line(
                    center_x - check_size/3, center_y,
                    center_x - check_size/6, center_y + check_size/3,
                    fill="#ffffff", width=6, capstyle=tk.ROUND
                )
                self.icon_canvas.create_line(
                    center_x - check_size/6, center_y + check_size/3,
                    center_x + check_size/2, center_y - check_size/3,
                    fill="#ffffff", width=6, capstyle=tk.ROUND
                )
                
                # Estrellas decorativas
                for i in range(4):
                    angle = (self.icon_rotation + i * 90) * math.pi / 180
                    star_x = center_x + math.cos(angle) * (radius + 20)
                    star_y = center_y + math.sin(angle) * (radius + 20)
                    star_size = 3 + 2 * math.sin(time.time() * 3 + i)
                    
                    self.icon_canvas.create_text(
                        star_x, star_y, text="✨", 
                        font=("Arial", int(star_size * 3)), fill="#f1c40f"
                    )
                
            else:
                # Círculo rojo con efectos
                # Aura externa
                aura_radius = radius + 10 + 5 * math.sin(time.time() * 4)
                alpha = int(50 + 30 * self.pulse_alpha)
                aura_color = f"#{255:02x}{alpha:02x}{alpha:02x}"
                
                self.icon_canvas.create_oval(
                    center_x - aura_radius, center_y - aura_radius,
                    center_x + aura_radius, center_y + aura_radius,
                    fill=aura_color, outline=""
                )
                
                # Círculo principal
                self.icon_canvas.create_oval(
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius,
                    fill="#e74c3c", outline="#c0392b", width=3
                )
                
                # X animada
                x_size = radius * 0.6
                self.icon_canvas.create_line(
                    center_x - x_size/2, center_y - x_size/2,
                    center_x + x_size/2, center_y + x_size/2,
                    fill="#ffffff", width=6, capstyle=tk.ROUND
                )
                self.icon_canvas.create_line(
                    center_x + x_size/2, center_y - x_size/2,
                    center_x - x_size/2, center_y + x_size/2,
                    fill="#ffffff", width=6, capstyle=tk.ROUND
                )
                
                # Partículas de advertencia
                for i in range(3):
                    angle = (self.icon_rotation * 2 + i * 120) * math.pi / 180
                    particle_x = center_x + math.cos(angle) * (radius + 15)
                    particle_y = center_y + math.sin(angle) * (radius + 15)
                    particle_size = 2 + math.sin(time.time() * 4 + i)
                    
                    self.icon_canvas.create_text(
                        particle_x, particle_y, text="⚠️", 
                        font=("Arial", int(particle_size * 2)), fill="#f39c12"
                    )
            
            # Efecto de brillo central
            highlight_radius = radius * 0.3
            self.icon_canvas.create_oval(
                center_x - highlight_radius, center_y - highlight_radius,
                center_x + highlight_radius, center_y + highlight_radius,
                fill="#ffffff", outline="", stipple="gray25"
            )
            
        except tk.TclError:
            pass
        
        # Continuar animación
        self.after(50, self.animate_icon)

    def animate_background(self):
        """Crea una animación espectacular en el fondo"""
        if not self.animation_running:
            return
            
        try:
            self.bg_canvas.delete("bg_effects")
            
            # Obtener dimensiones
            width = self.bg_canvas.winfo_width()
            height = self.bg_canvas.winfo_height()
            
            if width > 1 and height > 1:
                time_offset = time.time() * 0.5
                
                # Ondas de fondo
                for i in range(5):
                    wave_y = height * (0.2 + 0.15 * i) + 20 * math.sin(time_offset + i)
                    wave_amplitude = 30 + 10 * math.sin(time_offset * 0.7 + i)
                    
                    points = []
                    for x in range(0, width + 10, 10):
                        y = wave_y + wave_amplitude * math.sin((x / 50) + time_offset + i)
                        points.extend([x, y])
                    
                    if len(points) >= 4:
                        # Color basado en el éxito
                        if self.success:
                            alpha = int(20 + 10 * math.sin(time_offset + i))
                            color = f"#{alpha:02x}{alpha+30:02x}{alpha:02x}"
                        else:
                            alpha = int(20 + 10 * math.sin(time_offset + i))
                            color = f"#{alpha+30:02x}{alpha:02x}{alpha:02x}"
                        
                        self.bg_canvas.create_line(
                            points, fill=color, width=2, smooth=True,
                            tags="bg_effects"
                        )
                
                # Partículas flotantes
                for i in range(12):
                    x = (i * width / 12 + math.sin(time_offset + i) * 50) % width
                    y = (math.sin(time_offset * 0.8 + i * 0.5) * height * 0.4 + height * 0.5) % height
                    size = 4 + 3 * math.sin(time_offset * 2 + i)
                    
                    # Color y forma basados en el éxito
                    if self.success:
                        alpha = int(80 + 40 * math.sin(time_offset + i))
                        color = f"#{alpha:02x}{alpha+50:02x}{alpha:02x}"
                        shape = "✨" if i % 3 == 0 else "💚" if i % 3 == 1 else "⭐"
                    else:
                        alpha = int(80 + 40 * math.sin(time_offset + i))
                        color = f"#{alpha+50:02x}{alpha:02x}{alpha:02x}"
                        shape = "💔" if i % 3 == 0 else "⚠️" if i % 3 == 1 else "❌"
                    
                    if i % 2 == 0:  # Alternar entre círculos y emojis
                        self.bg_canvas.create_oval(
                            x - size, y - size, x + size, y + size,
                            fill=color, outline="", tags="bg_effects"
                        )
                    else:
                        self.bg_canvas.create_text(
                            x, y, text=shape, 
                            font=("Arial", int(size * 2)), 
                            fill=color, tags="bg_effects"
                        )
            
            self.after(100, self.animate_background)
            
        except tk.TclError:
            pass

    def animate_celebration(self):
        """Animación de celebración para compras exitosas"""
        if not self.animation_running or not self.success:
            return
            
        try:
            self.bg_canvas.delete("celebration")
            
            width = self.bg_canvas.winfo_width()
            height = self.bg_canvas.winfo_height()
            
            if width > 1 and height > 1:
                # Confetti cayendo
                if len(self.confetti_particles) < 20:
                    for _ in range(2):
                        self.confetti_particles.append({
                            'x': random.randint(0, width),
                            'y': -10,
                            'vx': random.uniform(-2, 2),
                            'vy': random.uniform(2, 5),
                            'color': random.choice(['#f1c40f', '#e74c3c', '#3498db', '#2ecc71', '#9b59b6']),
                            'size': random.randint(3, 8),
                            'rotation': random.uniform(0, 360)
                        })
                
                # Actualizar y dibujar confetti
                for particle in self.confetti_particles[:]:
                    particle['x'] += particle['vx']
                    particle['y'] += particle['vy']
                    particle['rotation'] += 5
                    
                    if particle['y'] > height + 10:
                        self.confetti_particles.remove(particle)
                        continue
                    
                    # Dibujar partícula de confetti
                    size = particle['size']
                    x, y = particle['x'], particle['y']
                    
                    self.bg_canvas.create_rectangle(
                        x - size/2, y - size/2, x + size/2, y + size/2,
                        fill=particle['color'], outline="", tags="celebration"
                    )
            
            self.after(100, self.animate_celebration)
            
        except tk.TclError:
            pass

    def start_countdown(self, seconds=5):
        """Inicia el contador regresivo con animación mejorada"""
        self.remaining = seconds
        self.total_seconds = seconds
        self.update_countdown()

        # Iniciar hilo para el contador
        self.countdown_thread = threading.Thread(target=self.run_countdown, daemon=True)
        self.countdown_thread.start()

    def run_countdown(self):
        """Ejecuta el contador regresivo (LÓGICA ORIGINAL)"""
        while self.remaining > 0:
            time.sleep(1)
            self.remaining -= 1
            try:
                self.after(0, self.update_countdown)
            except tk.TclError:
                break

        # Cuando termina el contador, volver a la pantalla de identificación
        try:
            self.after(0, self.on_return)
        except tk.TclError:
            pass

    def update_countdown(self):
        """Actualiza el contador regresivo con círculo de progreso espectacular"""
        try:
            # Actualizar texto
            self.countdown_label.config(text=f"Volviendo en {self.remaining} segundos...")
            
            # Actualizar círculo de progreso
            self.progress_canvas.delete("all")
            
            center_x, center_y = 40, 40
            radius = 30
            
            # Círculo de fondo con gradiente simulado
            for i in range(3):
                r = radius - i * 2
                alpha = 50 + i * 20
                color = f"#{alpha:02x}{alpha:02x}{alpha:02x}"
                self.progress_canvas.create_oval(
                    center_x - r, center_y - r,
                    center_x + r, center_y + r,
                    outline=color, width=1, fill=""
                )
            
            # Círculo de progreso
            if self.total_seconds > 0:
                progress = (self.total_seconds - self.remaining) / self.total_seconds
                extent = int(360 * progress)
                
                # Color basado en el éxito
                color = "#27ae60" if self.success else "#e74c3c"
                
                # Arco de progreso con efecto de brillo
                self.progress_canvas.create_arc(
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius,
                    start=90,  # Empezar desde arriba
                    extent=-extent,  # Sentido horario
                    style=tk.ARC,
                    outline=color,
                    width=4
                )
                
                # Efecto de brillo en el progreso
                if extent > 0:
                    highlight_color = "#ffffff"
                    self.progress_canvas.create_arc(
                        center_x - radius + 2, center_y - radius + 2,
                        center_x + radius - 2, center_y + radius - 2,
                        start=90,
                        extent=-min(extent, 30),  # Solo una pequeña parte brillante
                        style=tk.ARC,
                        outline=highlight_color,
                        width=2
                    )
            
            # Número en el centro con efectos
            # Fondo del número
            self.progress_canvas.create_oval(
                center_x - 15, center_y - 15,
                center_x + 15, center_y + 15,
                fill="#ffffff", outline=""
            )
            
            # Número principal
            self.progress_canvas.create_text(
                center_x, center_y,
                text=str(self.remaining), 
                font=("Segoe UI", 16, "bold"), 
                fill="#2c3e50"
            )
            
            # Efecto de pulso en el número
            pulse_size = 2 + math.sin(time.time() * 4)
            pulse_alpha = int(100 + 50 * math.sin(time.time() * 4))
            pulse_color = f"#{pulse_alpha:02x}{pulse_alpha:02x}{pulse_alpha:02x}"
            
            self.progress_canvas.create_oval(
                center_x - 15 - pulse_size, center_y - 15 - pulse_size,
                center_x + 15 + pulse_size, center_y - 15 + pulse_size,
                outline=pulse_color, width=1, fill=""
            )
            
        except tk.TclError:
            pass

    def destroy(self):
        """Limpieza completa al cerrar la pantalla"""
        self.animation_running = False
        
        # Limpiar partículas
        self.confetti_particles.clear()
        
        # Limpiar canvas
        try:
            self.bg_canvas.delete("all")
            self.icon_canvas.delete("all")
            self.progress_canvas.delete("all")
        except (tk.TclError, AttributeError):
            pass
        
        # Llamar al destructor padre
        super().destroy()
