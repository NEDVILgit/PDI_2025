import tkinter as tk
from tkinter import  messagebox, ttk
import numpy as np
from ui.base_frame import TPBaseFrame


class TP0Frame(TPBaseFrame):
  
        
    def _create_widgets(self):
        super()._create_widgets()
        ttk.Label(self, text="TP 0 - Interfaz", font=("Arial", 14, "bold")).pack(pady=10)
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
   
        # Modificación de píxeles   

        pixel_frame = ttk.LabelFrame(control_frame, text="Modificar Píxel", padding="10")
        pixel_frame.pack(fill=tk.X)

        labels = ["X:", "Y:", "R (0-255):", "G (0-255):", "B (0-255):"]
        self.entries = []
        for i, lbl in enumerate(labels):
            ttk.Label(pixel_frame, text=lbl).grid(row=i, column=0, sticky="w", pady=2)
            entry = ttk.Entry(pixel_frame)
            entry.grid(row=i, column=1, sticky="ew", pady=2)
            self.entries.append(entry)

        ttk.Button(pixel_frame, text="Aplicar Píxel", command=self._apply_pixel_modification).grid(row=5, columnspan=2, pady=5, sticky="ew")

        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

   
    def _apply_pixel_modification(self):
        x, y, r, g, b = [entry.get() for entry in self.entries]
        self.modificar_pixel(x, y, r, g, b)

    def modificar_pixel(self, x, y, r, g, b):
        if self.image_np is None:
            messagebox.showwarning("Advertencia", "Cargue una imagen primero.")
            return
        try:
            x, y, r, g, b = map(int, [x, y, r, g, b])
            if not (0 <= x < self.image_np.shape[1] and 0 <= y < self.image_np.shape[0]):
                raise ValueError("Coordenadas fuera de los límites.")
            if not all(0 <= val <= 255 for val in (r, g, b)):
                raise ValueError("Valores RGB deben estar entre 0 y 255.")
            if self.image_np.ndim == 2:  # escala de grises → RGB
                self.image_np = np.stack([self.image_np]*3, axis=-1)
            elif self.image_np.shape[2] == 4:  # ignorar alfa
                self.image_np = self.image_np[:, :, :3]
            self.image_np[y, x] = [r, g, b]
            self._update_image_display()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    

