import numpy as np
from tkinter import messagebox
import ttkbootstrap as ttk
from ui.base_frame import TPBaseFrame

class TP1Frame(TPBaseFrame):

       
    def _create_widgets(self):
        super()._create_widgets()
        ttk.Label(self, text="TP 1 - Conversion RGB a YIQ-YIQ' a RGB", font=("Arial", 14, "bold")).pack(pady=10)
        # Workflow YIQ
       
        workflow_frame = ttk.LabelFrame(self, text="Conversion y Modificacion", padding=5)
        workflow_frame.pack(side=ttk.LEFT, fill=ttk.X, padx=10)

        self.entries = []
        for param in ["Y","IQ"]:
            frame = ttk.Frame(workflow_frame)
            frame.pack(fill="x", pady=2)
            ttk.Label(frame, text=param).pack(side="left")
            entry = ttk.Entry(frame, width=5)
            entry.pack(side="right", padx=5)
            self.entries.append(entry)

        ttk.Button(workflow_frame, text="Mostrar YIQ", command=self.show_yiq).pack(pady=2, fill="x")
        ttk.Button(workflow_frame, text="Aplicar Modificación", command=self.apply_modification).pack(pady=2, fill="x")
        ttk.Button(workflow_frame, text="Mostrar RGB Modificado", command=self.show_modified_rgb).pack(pady=2, fill="x")
        ttk.Separator(workflow_frame, orient='horizontal').pack(fill='x', pady=10)

    def show_yiq(self):
        if self.image_np is None:
            messagebox.showwarning("Advertencia", "Cargue una imagen primero.")
            return
        self.yiq_image = self.rgb_to_yiq(self.image_np)
        self._update_image_display(self.yiq_image)

    def apply_modification(self):
        if self.image_np is None:
            messagebox.showwarning("Advertencia", "Cargue una imagen primero.")
            return
        try:
            a = float(self.entries[0].get())
            b = float(self.entries[1].get())
            self.modified_image = self.modify_image(self.image_np, a, b)
            messagebox.showinfo("Éxito", "Imagen modificada correctamente")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_modified_rgb(self):
        if hasattr(self, 'modified_image'):
            self._update_image_display(self.modified_image)
        else:
            messagebox.showwarning("Advertencia", "Aplique la modificación primero.")

    def rgb_to_yiq(self, img):
        img_norm = img / 255.0
        T = np.array([[0.299, 0.587, 0.114],
                      [0.596, -0.274, -0.322],
                      [0.211, -0.523, 0.312]])
        yiq = img_norm @ T.T
        return yiq

    def modify_image(self, img, a, b):
        yiq = self.rgb_to_yiq(img)
        y, i, q = yiq[...,0], yiq[...,1], yiq[...,2]

        y_mod = np.clip(a*y, 0, 1)
        i_mod = np.clip(b*i, -0.5957, 0.5957)
        q_mod = np.clip(b*q, -0.5226, 0.5226)

        yiq_mod = np.stack([y_mod, i_mod, q_mod], axis=-1)
        T_inv = np.array([[1, 0.956, 0.621],
                          [1, -0.272, -0.647],
                          [1, -1.106, 1.703]])
        rgb_mod = yiq_mod @ T_inv.T
        rgb_mod = np.clip(rgb_mod, 0, 1) * 255
        return rgb_mod.astype(np.uint8)
