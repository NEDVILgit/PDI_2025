import tkinter as tk
from ui.base_frame import TPBaseFrame


class TP0Frame(TPBaseFrame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Trabajo Práctico 0 - Interfaz", font=("Arial", 14, "bold")).pack(pady=10)
