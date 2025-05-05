import tkinter as tk

class WelcomeScreen(tk.Frame):
    def __init__(self, master, on_start_purchase, on_logout, user_data, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.on_start_purchase = on_start_purchase
        self.on_logout = on_logout
        self.user_data = user_data
        self.create_widgets()

    def create_widgets(self):
        nombre = self.user_data.get("nombre", "Usuario")
        saldo = self.user_data.get("saldo", 0.0)

        tk.Label(self, text=f"Bienvenido {nombre}", font=("Arial", 18)).pack(pady=10)
        tk.Label(self, text=f"Tu saldo es ${saldo:.2f}", font=("Arial", 14)).pack(pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Empezar compra", width=20, command=self.on_start_purchase).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Salir", width=20, command=self.on_logout).grid(row=0, column=1, padx=10)

# Prueba
if __name__ == "__main__":
    def start():
        print("[INFO] Comenzando proceso de compra...")

    def logout():
        print("[INFO] Sesión cerrada. Volviendo a identificación...")

    root = tk.Tk()
    root.title("Pantalla de Bienvenida")
    root.geometry("1280x800")
    root.overrideredirect(True)

    user_info = {"nombre": "Matías", "saldo": 1200.50}
    screen = WelcomeScreen(root, start, logout, user_info)
    screen.pack(fill="both", expand=True)

    root.mainloop()
