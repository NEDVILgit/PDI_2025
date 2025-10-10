import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import subprocess
import sys
import os
from tkinter import messagebox

class MenuPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Menú Principal de Trabajos Prácticos")
        self.root.geometry("600x420")
        self.root.resizable(False, False)

        # Estilo visual
        style = ttk.Style()
        style.configure('TButton', font=('Segoe UI', 12, 'bold'), padding=10)

        # Título principal
        title_label = ttk.Label(
            root,
            text="Seleccione un Trabajo Práctico",
            font=("Segoe UI", 20, "bold"),
            anchor="center"
        )
        title_label.pack(pady=40)

        # Frame central para botones
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=20)

        # Botones para abrir cada TP
        ttk.Button(
            button_frame,
            text="🧩 Abrir TP0",
            bootstyle=PRIMARY,
            width=20,
            command=lambda: self.abrir_tp("tps/tp0.py")
        ).pack(pady=10)

        ttk.Button(
            button_frame,
            text="📊 Abrir TP1",
            bootstyle=INFO,
            width=20,
            command=lambda: self.abrir_tp("tps/tp1.py")
        ).pack(pady=10)

        ttk.Button(
            button_frame,
            text="🖼️ Abrir TP2",
            bootstyle=SUCCESS,
            width=20,
            command=lambda: self.abrir_tp("tps/tp2.py")
        ).pack(pady=10)

        ttk.Separator(root, orient=HORIZONTAL).pack(fill=X, pady=20)

        # Botón de salida
        ttk.Button(
            root,
            text="❌ Salir",
            bootstyle=DANGER,
            width=15,
            command=self.root.destroy
        ).pack()

        # Pie de crédito
        footer = ttk.Label(
            root,
            text="Desarrollado por Cristian Alejandro Aguilera",
            font=("Segoe UI", 9),
            anchor="center",
            foreground="#AAAAAA"
        )
        footer.pack(side="bottom", pady=10)

    # ---------------------------
    # Método para abrir TP
    # ---------------------------
    def abrir_tp(self, script_name):
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        if not os.path.exists(script_path):
            messagebox.showerror("Error", f"No se encontró el archivo {script_name}")
            return

        # Ejecutar el TP como proceso independiente
        try:
            subprocess.Popen([sys.executable, script_path])
        except Exception as e:
            messagebox.showerror("Error al ejecutar", f"No se pudo abrir {script_name}.\n\nDetalles: {e}")

# ---------------------------
# Ejecución principal
# ---------------------------
if __name__ == "__main__":
    try:
        app = ttk.Window(themename="superhero")
    except Exception:
        import tkinter as tk
        app = tk.Tk()

    MenuPrincipal(app)
    app.mainloop()