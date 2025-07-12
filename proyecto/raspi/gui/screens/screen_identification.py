import tkinter as tk
from tkinter import font as tkfont
import math
import time
import random
import socket

from gui.types.auth_status import AuthStatus

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


class IdentificationScreen(tk.Frame):
    def __init__(self, master, auth_service, on_success, on_failure, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg="#f8f9fa")
        
        # Dependencias inyectadas
        self.auth_service = auth_service
        self.on_success = on_success
        self.on_failure = on_failure

        # Estado interno
        self._after_id = None
        self._scan_active = False
        self.processing = False
        self._spinner_angle = 0
        
        # Variables para animaciones
        self.animation_running = True
        self.wave_offset = 0
        self.pulse_scale = 1.0
        self.particles = []
        self.scan_rings = []
        self.logo_rotation = 0
        self.glow_intensity = 0
        
        # Crear fuentes personalizadas más elegantes
        self.title_font = tkfont.Font(family="Segoe UI", size=42, weight="bold")
        self.subtitle_font = tkfont.Font(family="Segoe UI", size=24, weight="normal")
        self.status_font = tkfont.Font(family="Segoe UI", size=18, weight="normal")
        self.instruction_font = tkfont.Font(family="Segoe UI", size=16, weight="normal")
        self.small_font = tkfont.Font(family="Segoe UI", size=12, weight="normal")
        
        # Construir UI completa
        self.create_full_ui()
        
        # Iniciar animaciones
        self.after(100, self.animate_background)
        self.after(200, self.animate_logo)
        
        # Iniciar escaneo después de mostrar la UI
        self.after(300, self.start_rfid_scan)

    def create_full_ui(self):
        """Construye la interfaz con diseño ultra moderno"""
        # Canvas principal para efectos de fondo
        self.bg_canvas = tk.Canvas(self, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Contenedor principal con efecto de elevación premium
        main_container = tk.Frame(self, bg="#ffffff")
        main_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.9)
        
        # Crear múltiples sombras para efecto de profundidad
        for i in range(4):
            shadow_intensity = 240 - i * 20
            shadow_color = f"#{shadow_intensity:02x}{shadow_intensity:02x}{shadow_intensity:02x}"
            shadow = tk.Frame(self, bg=shadow_color)
            shadow.place(relx=0.5, rely=0.5, anchor="center", 
                        relwidth=0.85 + i*0.008, relheight=0.9 + i*0.008)
        
        main_container.lift()
        
        # Canvas para gradiente en el contenedor principal
        gradient_canvas = tk.Canvas(main_container, highlightthickness=0)
        gradient_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Crear gradiente de fondo
        self.create_gradient_background(gradient_canvas)
        
        # Contenido principal
        content_frame = tk.Frame(main_container, bg="#ffffff")
        content_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
        
        # Header con logo animado y título
        header_frame = tk.Frame(content_frame, bg="#ffffff", height=180)
        header_frame.pack(fill="x", pady=(20, 0))
        header_frame.pack_propagate(False)
        
        # Logo con animación espectacular
        logo_container = tk.Frame(header_frame, bg="#ffffff", height=120)
        logo_container.pack()
        logo_container.pack_propagate(False)
        
        # Canvas para el logo animado
        self.logo_canvas = tk.Canvas(logo_container, width=120, height=120, 
                                    bg="#ffffff", highlightthickness=0)
        self.logo_canvas.pack()
        
        # Título principal con efectos
        title_container = tk.Frame(header_frame, bg="#ffffff")
        title_container.pack(pady=(10, 0))
        
        self.title_label = tk.Label(
            title_container, text="AUTOCASHIER", font=self.title_font, 
            bg="#ffffff", fg="#2c3e50"
        )
        self.title_label.pack()
        
        # Subtítulo elegante
        subtitle_label = tk.Label(
            title_container, text="Sistema de Compras Inteligente", 
            font=tkfont.Font(family="Segoe UI", size=16, weight="normal"),
            bg="#ffffff", fg="#7f8c8d"
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Línea separadora animada
        separator_frame = tk.Frame(content_frame, bg="#ffffff", height=20)
        separator_frame.pack(fill="x", pady=15)
        separator_frame.pack_propagate(False)
        
        self.separator_canvas = tk.Canvas(separator_frame, height=4, bg="#ffffff", highlightthickness=0)
        self.separator_canvas.pack(fill="x")
        
        # Sección de instrucciones con diseño premium
        instruction_section = tk.Frame(content_frame, bg="#f8f9fa", padx=30, pady=25)
        instruction_section.pack(fill="x", pady=(0, 30))
        
        # Borde elegante para la sección
        instruction_section.config(relief="solid", bd=1, highlightbackground="#e1e8ed", highlightthickness=1)
        
        # Título de la sección
        section_title = tk.Label(
            instruction_section,
            text="🔐 Identificación de Usuario",
            font=tkfont.Font(family="Segoe UI", size=20, weight="bold"),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        section_title.pack(pady=(0, 15))
        
        # Instrucciones con ícono visual mejorado
        instruction_frame = tk.Frame(instruction_section, bg="#f8f9fa")
        instruction_frame.pack()
        
        # Canvas para el ícono de tarjeta animado
        self.card_canvas = tk.Canvas(instruction_frame, width=80, height=50, 
                                   bg="#f8f9fa", highlightthickness=0)
        self.card_canvas.pack(side=tk.LEFT, padx=(0, 20))
        
        # Contenedor para texto de instrucciones
        text_container = tk.Frame(instruction_frame, bg="#f8f9fa")
        text_container.pack(side=tk.LEFT, fill="both", expand=True)
        
        self.instruction_label = tk.Label(
            text_container,
            text="Acerca tu tarjeta al lector RFID",
            font=self.subtitle_font,
            bg="#f8f9fa",
            fg="#2c3e50",
        )
        self.instruction_label.pack(anchor="w")
        
        # Descripción adicional
        description_label = tk.Label(
            text_container,
            text="El sistema detectará automáticamente tu tarjeta y te dará acceso",
            font=self.instruction_font,
            bg="#f8f9fa",
            fg="#7f8c8d",
        )
        description_label.pack(anchor="w", pady=(5, 0))
        
        # Área de escaneo con efectos espectaculares
        scan_area = tk.Frame(content_frame, bg="#ffffff", height=200)
        scan_area.pack(fill="x", pady=(0, 30))
        scan_area.pack_propagate(False)
        
        # Canvas principal para efectos de escaneo
        self.scan_canvas = tk.Canvas(scan_area, height=200, bg="#ffffff", highlightthickness=0)
        self.scan_canvas.pack(fill="both", expand=True)
        
        # Estado con diseño futurista
        status_container = tk.Frame(content_frame, bg="#ffffff")
        status_container.pack(fill="x", pady=(0, 20))
        
        # Frame para el estado con efectos
        status_frame = tk.Frame(status_container, bg="#f0f9ff", padx=25, pady=20)
        status_frame.pack()
        
        # Borde elegante para el estado
        status_frame.config(relief="solid", bd=1, highlightbackground="#3498db", highlightthickness=2)
        
        # Canvas para indicador de estado
        self.status_indicator = tk.Canvas(status_frame, width=20, height=20, 
                                        bg="#f0f9ff", highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 15))
        
        self.status_label = tk.Label(
            status_frame,
            text="Preparando lector...",
            font=self.status_font,
            bg="#f0f9ff",
            fg="#3498db"
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Pie de página con información adicional
        footer_frame = tk.Frame(content_frame, bg="#f8f9fa", height=60)
        footer_frame.pack(side=tk.BOTTOM, fill="x")
        footer_frame.pack_propagate(False)
        
        # Canvas para línea decorativa en el footer
        footer_canvas = tk.Canvas(footer_frame, height=2, bg="#f8f9fa", highlightthickness=0)
        footer_canvas.pack(fill="x", pady=(15, 10))
        
        self.create_decorative_line(footer_canvas, "#3498db")
        
        # Información del footer
        footer_info = tk.Label(
            footer_frame,
            text="🛡️ Conexión segura • 🔄 Escaneo automático • ⚡ Respuesta instantánea",
            font=self.small_font,
            bg="#f8f9fa",
            fg="#95a5a6"
        )
        footer_info.pack()
        
        # Inicializar animaciones
        self.animate_card_icon()
        self.animate_separator()
        self.animate_scan_area()

    def create_gradient_background(self, canvas):
        """Crea un gradiente de fondo elegante"""
        canvas.update_idletasks()
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width > 1 and height > 1:
            # Gradiente sutil de blanco a azul muy claro
            color1, color2 = "#ffffff", "#f8fbff"
            
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
        """Anima el fondo con partículas sutiles"""
        if not self.animation_running:
            return
            
        try:
            self.bg_canvas.delete("bg_particles")
            
            width = self.bg_canvas.winfo_width()
            height = self.bg_canvas.winfo_height()
            
            if width > 1 and height > 1:
                time_offset = time.time() * 0.3
                
                # Partículas flotantes sutiles
                for i in range(15):
                    x = (i * width / 15 + math.sin(time_offset + i) * 40) % width
                    y = (math.sin(time_offset * 0.6 + i * 0.4) * height * 0.3 + height * 0.5) % height
                    size = 2 + math.sin(time_offset + i) * 1
                    
                    alpha = int(30 + 20 * math.sin(time_offset + i))
                    color = f"#{alpha:02x}{alpha:02x}{alpha+30:02x}"
                    
                    self.bg_canvas.create_oval(
                        x - size, y - size, x + size, y + size,
                        fill=color, outline="", tags="bg_particles"
                    )
            
            self.after(100, self.animate_background)
        except tk.TclError:
            pass

    def animate_logo(self):
        """Anima el logo con efectos espectaculares"""
        if not self.animation_running:
            return
            
        try:
            self.logo_canvas.delete("all")
            
            center_x, center_y = 60, 60
            time_offset = time.time()
            
            # Actualizar variables de animación
            self.logo_rotation += 1
            self.pulse_scale = 1.0 + 0.1 * math.sin(time_offset * 2)
            self.glow_intensity = (math.sin(time_offset * 3) + 1) / 2
            
            # Aura externa pulsante
            aura_radius = 45 + 10 * math.sin(time_offset * 4)
            alpha = int(30 + 20 * self.glow_intensity)
            aura_color = f"#{alpha:02x}{alpha:02x}{alpha+50:02x}"
            
            self.logo_canvas.create_oval(
                center_x - aura_radius, center_y - aura_radius,
                center_x + aura_radius, center_y + aura_radius,
                fill=aura_color, outline=""
            )
            
            # Anillos orbitales
            for i in range(3):
                ring_radius = 35 + i * 8
                ring_alpha = int(100 + 50 * math.sin(time_offset * 2 + i))
                ring_color = f"#{ring_alpha:02x}{ring_alpha:02x}{ring_alpha+100:02x}"
                
                self.logo_canvas.create_oval(
                    center_x - ring_radius, center_y - ring_radius,
                    center_x + ring_radius, center_y + ring_radius,
                    outline=ring_color, width=1, fill=""
                )
            
            # Círculo principal con gradiente simulado
            main_radius = 30 * self.pulse_scale
            
            # Múltiples círculos para simular gradiente
            for i in range(5):
                radius = main_radius - i * 2
                intensity = 52 + i * 10  # De azul oscuro a azul claro
                color = f"#{intensity:02x}{intensity+50:02x}{255:02x}"
                
                self.logo_canvas.create_oval(
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius,
                    fill=color, outline=""
                )
            
            # Texto del logo con efectos
            self.logo_canvas.create_text(
                center_x, center_y, text="AC", 
                font=tkfont.Font(family="Segoe UI", size=int(24 * self.pulse_scale), weight="bold"), 
                fill="#ffffff"
            )
            
            # Partículas orbitales
            for i in range(6):
                angle = (self.logo_rotation * 2 + i * 60) * math.pi / 180
                orbit_radius = 50 + 5 * math.sin(time_offset * 3 + i)
                particle_x = center_x + math.cos(angle) * orbit_radius
                particle_y = center_y + math.sin(angle) * orbit_radius
                particle_size = 2 + math.sin(time_offset * 4 + i)
                
                self.logo_canvas.create_oval(
                    particle_x - particle_size, particle_y - particle_size,
                    particle_x + particle_size, particle_y + particle_size,
                    fill="#f1c40f", outline=""
                )
            
            self.after(50, self.animate_logo)
        except tk.TclError:
            pass

    def animate_card_icon(self):
        """Anima el ícono de la tarjeta"""
        if not self.animation_running:
            return
            
        try:
            self.card_canvas.delete("all")
            
            time_offset = time.time()
            hover_offset = 3 * math.sin(time_offset * 2)
            glow = int(100 + 50 * math.sin(time_offset * 3))
            
            # Sombra de la tarjeta
            shadow_color = f"#{glow:02x}{glow:02x}{glow:02x}"
            self.card_canvas.create_rectangle(
                12, 18 + hover_offset, 68, 38 + hover_offset, 
                fill=shadow_color, outline=""
            )
            
            # Tarjeta principal
            self.card_canvas.create_rectangle(
                10, 15 + hover_offset, 65, 35 + hover_offset, 
                fill="#3498db", outline="#2980b9", width=2
            )
            
            # Chip de la tarjeta
            self.card_canvas.create_rectangle(
                20, 22 + hover_offset, 35, 28 + hover_offset, 
                fill="#f1c40f", outline="#f39c12", width=1
            )
            
            # Líneas de datos
            for i in range(2):
                y_pos = 30 + i * 3 + hover_offset
                self.card_canvas.create_line(
                    40, y_pos, 60, y_pos, 
                    fill="#ecf0f1", width=1
                )
            
            # Efecto de brillo
            highlight_alpha = int(150 + 50 * math.sin(time_offset * 4))
            highlight_color = f"#{highlight_alpha:02x}{highlight_alpha:02x}{255:02x}"
            self.card_canvas.create_line(
                15, 20 + hover_offset, 25, 20 + hover_offset, 
                fill=highlight_color, width=2
            )
            
            self.after(50, self.animate_card_icon)
        except tk.TclError:
            pass

    def animate_separator(self):
        """Anima la línea separadora"""
        if not self.animation_running:
            return
            
        try:
            self.separator_canvas.delete("all")
            
            width = self.separator_canvas.winfo_width()
            if width > 1:
                time_offset = time.time()
                
                # Línea base
                self.separator_canvas.create_rectangle(
                    0, 1, width, 3, fill="#e1e8ed", outline=""
                )
                
                # Efecto de onda que se mueve
                wave_pos = (time_offset * 100) % (width + 100)
                wave_width = 50
                
                for i in range(wave_width):
                    x = wave_pos - wave_width/2 + i
                    if 0 <= x < width:
                        alpha = math.sin(math.pi * i / wave_width)
                        intensity = int(52 + 100 * alpha)
                        color = f"#{intensity:02x}{intensity+50:02x}{255:02x}"
                        self.separator_canvas.create_line(x, 1, x, 3, fill=color)
            
            self.after(100, self.animate_separator)
        except tk.TclError:
            pass

    def animate_scan_area(self):
        """Anima el área de escaneo con efectos futuristas"""
        if not self.animation_running:
            return
            
        try:
            self.scan_canvas.delete("scan_effects")
            
            width = self.scan_canvas.winfo_width()
            height = self.scan_canvas.winfo_height()
            
            if width > 1 and height > 1:
                center_x, center_y = width / 2, height / 2
                time_offset = time.time()
                
                # Anillos de escaneo concéntricos
                for i in range(4):
                    radius = 30 + i * 20 + 10 * math.sin(time_offset * 2 + i)
                    alpha = int(100 - i * 20 + 50 * math.sin(time_offset * 3 + i))
                    if alpha > 0:
                        color = f"#{alpha:02x}{alpha:02x}{alpha+100:02x}"
                        self.scan_canvas.create_oval(
                            center_x - radius, center_y - radius,
                            center_x + radius, center_y + radius,
                            outline=color, width=2, tags="scan_effects"
                        )
                
                # Líneas de escaneo radiales
                for i in range(8):
                    angle = (time_offset * 50 + i * 45) * math.pi / 180
                    length = 60 + 20 * math.sin(time_offset * 2 + i)
                    end_x = center_x + math.cos(angle) * length
                    end_y = center_y + math.sin(angle) * length
                    
                    alpha = int(150 + 50 * math.sin(time_offset * 4 + i))
                    color = f"#{alpha:02x}{alpha:02x}{255:02x}"
                    
                    self.scan_canvas.create_line(
                        center_x, center_y, end_x, end_y,
                        fill=color, width=1, tags="scan_effects"
                    )
                
                # Partículas de datos flotantes
                for i in range(12):
                    particle_angle = (time_offset * 30 + i * 30) * math.pi / 180
                    particle_radius = 80 + 20 * math.sin(time_offset + i)
                    particle_x = center_x + math.cos(particle_angle) * particle_radius
                    particle_y = center_y + math.sin(particle_angle) * particle_radius
                    
                    if 0 <= particle_x <= width and 0 <= particle_y <= height:
                        size = 2 + math.sin(time_offset * 3 + i)
                        alpha = int(100 + 50 * math.sin(time_offset * 2 + i))
                        color = f"#{alpha:02x}{alpha+50:02x}{255:02x}"
                        
                        self.scan_canvas.create_oval(
                            particle_x - size, particle_y - size,
                            particle_x + size, particle_y + size,
                            fill=color, outline="", tags="scan_effects"
                        )
            
            self.after(50, self.animate_scan_area)
        except tk.TclError:
            pass

    def animate_status_indicator(self, color="#3498db"):
        """Anima el indicador de estado"""
        try:
            self.status_indicator.delete("all")
            
            time_offset = time.time()
            pulse = 0.5 + 0.5 * math.sin(time_offset * 4)
            size = 6 + 4 * pulse
            
            # Círculo pulsante
            self.status_indicator.create_oval(
                10 - size, 10 - size, 10 + size, 10 + size,
                fill=color, outline=""
            )
            
            # Anillo exterior
            ring_size = size + 3
            alpha = int(100 * pulse)
            ring_color = f"#{alpha:02x}{alpha:02x}{alpha+100:02x}"
            
            self.status_indicator.create_oval(
                10 - ring_size, 10 - ring_size, 10 + ring_size, 10 + ring_size,
                outline=ring_color, width=1
            )
            
        except tk.TclError:
            pass

    def start_rfid_scan(self):
        """Inicia el proceso de escaneo RFID (LÓGICA ORIGINAL)"""
        if self._scan_active:
            return

        self._scan_active = True
        self.status_label.config(text="🔍 Buscando tarjeta...", fg="#3498db")
        self.animate_status_indicator("#3498db")
        self._check_rfid()

    def _check_rfid(self):
        """Verificación periódica del lector RFID (LÓGICA ORIGINAL)"""
        if not self._scan_active:
            return

        try:
            status, user = self.auth_service.authenticate_user()

            if status == AuthStatus.NO_CARD:
                # No hacer nada
                pass
            elif status == AuthStatus.UNAUTHORIZED:
                self._handle_failure()
            elif status == AuthStatus.AUTHORIZED:
                self._handle_success(user)

        except Exception as e:
            self._handle_error(str(e))

        finally:
            if self._scan_active:
                self._after_id = self.after(1000, self._check_rfid)

    def _handle_success(self, user):
        """Tarjeta detectada correctamente con animación espectacular"""
        try:
            # Notificar éxito al proceso GPIO
            send_gpio_feedback("SUCCESS")
            # Actualizar UI con efectos de éxito
            self.status_label.config(text="✅ ¡Tarjeta reconocida!", fg="#27ae60")
            self.instruction_label.config(text="Acceso concedido - Bienvenido", fg="#27ae60")
            self.animate_status_indicator("#27ae60")

            # Efecto de éxito en el área de escaneo
            self.scan_canvas.delete("scan_effects")
            width = self.scan_canvas.winfo_width()
            height = self.scan_canvas.winfo_height()
            center_x, center_y = width / 2, height / 2
            
            # Círculo de éxito expandiéndose
            for i in range(5):
                radius = 20 + i * 15
                alpha = int(150 - i * 20)
                color = f"#{alpha:02x}{255:02x}{alpha:02x}"
                self.scan_canvas.create_oval(
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius,
                    outline=color, width=3, tags="success_effect"
                )
            
            # Checkmark central
            self.scan_canvas.create_text(
                center_x, center_y, text="✓", 
                font=tkfont.Font(size=48, weight="bold"), 
                fill="#27ae60", tags="success_effect"
            )

            # Preparar datos y callback (LÓGICA ORIGINAL)
            user_data = {
                "nombre": user.username,
                "apellido": user.surname,
                "saldo": user.balance,
                "external_id": user.external_id,
            }

            # Transición después de un breve momento
            self.after(350, lambda: self.on_success(user_data))
        except Exception as e:
            print(f"Error en _handle_success: {e}")

    def _handle_failure(self):
        """Maneja cuando no se reconoce una tarjeta con efectos visuales impactantes"""
        try:
            # Notificar fallo al proceso GPIO
            send_gpio_feedback("FAILURE")
            # Cancelar cualquier temporizador previo
            if hasattr(self, "_restore_timer"):
                self.after_cancel(self._restore_timer)

            # Actualizar UI con efectos de error
            self.status_label.config(text="❌ USUARIO NO RECONOCIDO", fg="#e74c3c")
            self.instruction_label.config(text="Retire la tarjeta e intente nuevamente", fg="#e74c3c")
            self.animate_status_indicator("#e74c3c")
            
            # Efecto de error en el área de escaneo
            self.scan_canvas.delete("scan_effects")
            width = self.scan_canvas.winfo_width()
            height = self.scan_canvas.winfo_height()
            center_x, center_y = width / 2, height / 2
            
            # Círculo de error pulsante
            for i in range(3):
                radius = 30 + i * 20
                alpha = int(200 - i * 50)
                color = f"#{255:02x}{alpha:02x}{alpha:02x}"
                self.scan_canvas.create_oval(
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius,
                    outline=color, width=4, tags="error_effect"
                )
            
            # X central
            size = 25
            self.scan_canvas.create_line(
                center_x - size, center_y - size, center_x + size, center_y + size,
                fill="#e74c3c", width=6, tags="error_effect"
            )
            self.scan_canvas.create_line(
                center_x + size, center_y - size, center_x - size, center_y + size,
                fill="#e74c3c", width=6, tags="error_effect"
            )

            # Forzar actualización inmediata de la interfaz
            self.update_idletasks()

            # Función para restaurar el estado (LÓGICA ORIGINAL)
            def restore_state():
                try:
                    # Restaurar textos y colores originales
                    self.status_label.config(text="🔍 Acerca tu tarjeta al lector", fg="#3498db")
                    self.instruction_label.config(text="Acerca tu tarjeta al lector RFID", fg="#2c3e50")
                    self.animate_status_indicator("#3498db")

                    # Limpiar efectos de error
                    self.scan_canvas.delete("error_effect")

                    # Reiniciar estado de escaneo
                    if hasattr(self, '_current_external_id'):
                        self._current_external_id = None
                    if hasattr(self, '_card_processing'):
                        self._card_processing = False

                    # Reiniciar escaneo si está activo
                    if self._scan_active:
                        self._after_id = self.after(100, self._check_rfid)
                except tk.TclError:
                    pass

            # Programar la restauración después de 1.5 segundos
            self._restore_timer = self.after(1500, restore_state)
        except Exception as e:
            print(f"Error en _handle_failure: {e}")

    def _handle_error(self, error_msg):
        """Error en el lector con visualización mejorada"""
        try:
            # Actualizar UI con efectos de advertencia
            self.status_label.config(text=f"⚠️ Error: {error_msg}", fg="#f39c12")
            self.instruction_label.config(text="Verificando conexión del lector...", fg="#f39c12")
            self.animate_status_indicator("#f39c12")
            
            # Efecto de advertencia en el área de escaneo
            self.scan_canvas.delete("scan_effects")
            width = self.scan_canvas.winfo_width()
            height = self.scan_canvas.winfo_height()
            center_x, center_y = width / 2, height / 2
            
            # Triángulo de advertencia
            size = 30
            self.scan_canvas.create_polygon(
                center_x, center_y - size,
                center_x - size, center_y + size,
                center_x + size, center_y + size,
                fill="#f39c12", outline="#e67e22", width=2, tags="warning_effect"
            )
            
            # Signo de exclamación
            self.scan_canvas.create_text(
                center_x, center_y + 5, text="!", 
                font=tkfont.Font(size=32, weight="bold"), 
                fill="#ffffff", tags="warning_effect"
            )
            
            print(f"RFID Error: {error_msg}")
        except Exception as e:
            print(f"Error en _handle_error: {e}")

    def destroy(self):
        """Limpieza completa al cerrar la pantalla"""
        self.animation_running = False
        self._scan_active = False
        
        # Cancelar todos los temporizadores
        if hasattr(self, "_after_id") and self._after_id:
            self.after_cancel(self._after_id)
        if hasattr(self, "_restore_timer") and self._restore_timer:
            self.after_cancel(self._restore_timer)
        
        # Limpiar canvas
        try:
            self.bg_canvas.delete("all")
            self.logo_canvas.delete("all")
            self.scan_canvas.delete("all")
            self.card_canvas.delete("all")
            self.separator_canvas.delete("all")
            self.status_indicator.delete("all")
        except (tk.TclError, AttributeError):
            pass
        
        # Llamar al destructor padre
        super().destroy()