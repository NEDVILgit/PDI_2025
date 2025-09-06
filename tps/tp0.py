from tkinter import ttk, messagebox
import numpy as np
from ui.base_frame import TPBaseFrame


class TP0Frame(TPBaseFrame):
    def __init__(self, parent):
        super().__init__(parent)

    def _create_widgets(self):
        super()._create_widgets()

        # Controles de modificación de píxel
        pixel_frame = ttk.LabelFrame(self.control_frame, text="Modificar Píxel", padding=10)
        pixel_frame.pack(fill="x", pady=10)

        ttk.Label(pixel_frame, text="X:").grid(row=0, column=0)
        self.x_entry = ttk.Entry(pixel_frame, width=5)
        self.x_entry.grid(row=0, column=1)

        ttk.Label(pixel_frame, text="Y:").grid(row=1, column=0)
        self.y_entry = ttk.Entry(pixel_frame, width=5)
        self.y_entry.grid(row=1, column=1)

        ttk.Label(pixel_frame, text="R:").grid(row=2, column=0)
        self.r_entry = ttk.Entry(pixel_frame, width=5)
        self.r_entry.grid(row=2, column=1)

        ttk.Label(pixel_frame, text="G:").grid(row=3, column=0)
        self.g_entry = ttk.Entry(pixel_frame, width=5)
        self.g_entry.grid(row=3, column=1)

        ttk.Label(pixel_frame, text="B:").grid(row=4, column=0)
        self.b_entry = ttk.Entry(pixel_frame, width=5)
        self.b_entry.grid(row=4, column=1)

        ttk.Button(pixel_frame, text="Aplicar", command=self._apply_pixel_modification).grid(row=5, columnspan=2, pady=5)

    def _apply_pixel_modification(self):
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            r = int(self.r_entry.get())
            g = int(self.g_entry.get())
            b = int(self.b_entry.get())

            if self.image_np is None:
                messagebox.showwarning("Advertencia", "No hay imagen cargada.")
                return
            if not (0 <= x < self.image_np.shape[1] and 0 <= y < self.image_np.shape[0]):
                messagebox.showerror("Error", "Coordenadas fuera de rango.")
                return

            if self.image_np.ndim == 2:
                self.image_np = np.stack([self.image_np]*3, axis=-1)
            elif self.image_np.shape[2] == 4:
                self.image_np = self.image_np[:, :, :3]

            self.image_np[y, x] = [r, g, b]
            self.current_image_title = f"Píxel ({x},{y}) Modificado"
            self._update_image_display()
        except Exception as e:
            messagebox.showerror("Error", str(e))
