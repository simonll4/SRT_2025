import tkinter as tk
from tkinter import font as tkfont

from gui.types.auth_status import AuthStatus


class IdentificationScreen(tk.Frame):
    def __init__(self, master, auth_service, on_success, on_failure, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg="#ffffff", padx=40, pady=40)

        # Dependencias inyectadas
        self.auth_service = auth_service
        self.on_success = on_success
        self.on_failure = on_failure

        # Estado interno
        self._after_id = None
        self._scan_active = False  # Inicialmente inactivo
        self.processing = False  # Estado de procesamiento

        # Elementos UI
        self.title_label = None
        self.instruction_label = None
        self.status_label = None
        self.canvas = None

        # Construir UI completa inmediatamente
        self.create_full_ui()

        # Iniciar escaneo después de mostrar la UI
        self.after(100, self.start_rfid_scan)

    def create_full_ui(self):
        """Construye TODA la interfaz inmediatamente al crear la pantalla"""
        # Configuración de fuentes
        title_font = tkfont.Font(family="Helvetica", size=24, weight="bold")
        instruction_font = tkfont.Font(family="Helvetica", size=18)
        status_font = tkfont.Font(family="Helvetica", size=16)

        # 1. Título principal (siempre visible)
        self.title_label = tk.Label(
            self, text="AUTOCASHIER", font=title_font, bg="#ffffff", fg="#333333"
        )
        self.title_label.pack(pady=(20, 10))

        # 2. Instrucciones (visibles desde el inicio)
        self.instruction_label = tk.Label(
            self,
            text="Acerca tu tarjeta al lector RFID",
            font=instruction_font,
            bg="#ffffff",
            fg="#555555",
        )
        self.instruction_label.pack(pady=10)

        # 3. Canvas para spinner/icono
        self.canvas = tk.Canvas(
            self, width=60, height=60, bg="#ffffff", highlightthickness=0
        )
        self.canvas.pack()

        # 4. Estado (visible desde el inicio)
        self.status_label = tk.Label(
            self,
            text="Preparando lector...",
            font=status_font,
            bg="#ffffff",
            fg="#007acc",
        )
        self.status_label.pack(pady=20)

        # Dibujar spinner inicial
        self._draw_spinner()

    def start_rfid_scan(self):
        """Inicia el proceso de escaneo RFID"""
        if self._scan_active:
            return

        self._scan_active = True
        self.status_label.config(text="Buscando tarjeta...", fg="#007acc")
        self._check_rfid()

    def _draw_spinner(self, angle=0):
        """Animación de spinner continuo"""
        self.canvas.delete("all")
        self.canvas.create_arc(
            10,
            10,
            50,
            50,
            start=angle,
            extent=120,
            style=tk.ARC,
            outline="#007acc",
            width=4,
        )
        self._spinner_id = self.after(
            50, lambda: self._draw_spinner((angle + 30) % 360)
        )

    def _check_rfid(self):
        """Verificación periódica del lector RFID"""
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
        """Tarjeta detectada correctamente"""
        # 1. Actualizar UI
        self.status_label.config(text="¡Tarjeta reconocida!", fg="#28a745")
        self.instruction_label.config(fg="#28a745")

        # TODO abrir socket para prender luz verde y ruido de ok

        # 2. Detener spinner y mostrar checkmark
        self.after_cancel(self._spinner_id)
        self.canvas.delete("all")
        self.canvas.create_oval(10, 10, 50, 50, fill="#28a745", outline="")
        self.canvas.create_text(
            30, 30, text="✓", font=tkfont.Font(size=24), fill="#ffffff"
        )

        # 3. Preparar datos y callback
        user_data = {
            "nombre": user.username,
            "apellido": user.surname,
            "saldo": user.balance,
            "external_id": user.external_id,
        }

        # 4. Transición después de 1.5 segundos
        self.after(350, lambda: self.on_success(user_data))

    def _handle_failure(self):
        """Maneja cuando no se reconoce una tarjeta"""

        # TODO abrir socket para prender luz roja y ruido de error

        # 1. Cancelar cualquier temporizador previo
        if hasattr(self, "_restore_timer"):
            self.after_cancel(self._restore_timer)

        # 2. Mostrar mensaje de error
        self.status_label.config(text="USUARIO NO RECONOCIDO", fg="#dc3545")  # Rojo
        self.instruction_label.config(
            text="Retire la tarjeta e intente nuevamente", fg="#dc3545"
        )

        # Forzar actualización inmediata de la interfaz
        self.update_idletasks()
        self.update()

        # 3. Función para restaurar el estado
        def restore_state():
            # Restaurar textos y colores originales
            self.status_label.config(text="Acerca tu tarjeta al lector", fg="#007acc")
            self.instruction_label.config(
                text="Acerca tu tarjeta al lector RFID", fg="#555555"
            )

            # Reiniciar estado de escaneo
            self._current_external_id = None
            self._card_processing = False

            # Forzar actualización
            self.update_idletasks()
            self.update()

            # Reiniciar escaneo si está activo
            if self._scan_active:
                self._after_id = self.after(100, self._check_rfid)

        # 4. Programar la restauración después de 1 segundo
        self._restore_timer = self.after(1000, restore_state)

        # 5. Forzar actualización inmediata
        self.update_idletasks()
        self.update()

    def _handle_error(self, error_msg):
        """Error en el lector"""
        self.status_label.config(text=f"Error: {error_msg}", fg="#ffc107")
        self.instruction_label.config(fg="#ffc107")
        print(f"RFID Error: {error_msg}")

    def destroy(self):
        """Limpieza al cerrar la pantalla"""
        self._scan_active = False
        if hasattr(self, "_after_id"):
            self.after_cancel(self._after_id)
        if hasattr(self, "_spinner_id"):
            self.after_cancel(self._spinner_id)
        super().destroy()

    # TODO para interactuar con el feedback de GPIO
    # import socket
    # def send_gpio_feedback(command: str):
    #     try:
    #         with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
    #             client.connect("/tmp/gpio_feedback.sock")
    #             client.sendall(command.encode("utf-8"))
    #     except Exception as e:
    #         print(f"[GPIO_FEEDBACK] Error al enviar comando: {e}")
    # send_gpio_feedback("SUCCESS")
    # send_gpio_feedback("FAILURE")
