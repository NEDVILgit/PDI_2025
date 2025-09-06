import numpy as np
from tkinter import messagebox
import ttkbootstrap as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from ui.base_frame import TPBaseFrame


class TP1Frame(TPBaseFrame):
    def __init__(self, parent):
        # Inicializo primero los atributos extra
        self.yiq_image = None
        self.modified_image = None

        # Ahora sí llamo al constructor del padre
        super().__init__(parent)

    # ---------------- Widgets ----------------
    def _create_widgets(self):
        super()._create_widgets()
        ttk.Label(self, text="TP 1 - Conversión RGB ↔ YIQ", font=("Arial", 14, "bold")).pack(pady=10)

        # Panel Workflow
        workflow_frame = ttk.LabelFrame(self, text="Conversión y Modificación", padding=5)
        workflow_frame.pack(side=ttk.LEFT, fill=ttk.X, padx=10)

        self.entries = []
        for param in ["Y", "IQ"]:
            frame = ttk.Frame(workflow_frame)
            frame.pack(fill="x", pady=2)
            ttk.Label(frame, text=param).pack(side="left")
            entry = ttk.Entry(frame, width=5)
            entry.pack(side="right", padx=5)
            self.entries.append(entry)

        ttk.Button(workflow_frame, text="Mostrar YIQ", command=self.mostrarYIQ).pack(pady=2, fill="x")
        ttk.Button(workflow_frame, text="Aplicar Modificación", command=self.modYIQ).pack(pady=2, fill="x")
        ttk.Button(workflow_frame, text="Mostrar RGB Modificado", command=self.show_modified_rgb).pack(pady=2, fill="x")

    # ---------------- Canvases ----------------
    def _setup_matplotlib_canvases(self):
        self.images_frame = ttk.Frame(self)
        self.images_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # --- Panel Original ---
        original_panel = ttk.LabelFrame(self.images_frame, text="Imagen Original", padding=5)
        original_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.fig_original = Figure(figsize=(3.5, 3), dpi=100)
        self.ax_original = self.fig_original.add_subplot(111)
        self.canvas_original = FigureCanvasTkAgg(self.fig_original, master=original_panel)
        self.canvas_original.get_tk_widget().pack(side="top", fill="both", expand=True)

        # Toolbar e info
        self.toolbar_original = NavigationToolbar2Tk(self.canvas_original, original_panel)
        self.toolbar_original.update()
        self.label_original_info = ttk.Label(original_panel, text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.label_original_info.pack(pady=5)

        # --- Panel YIQ ---
        yiq_panel = ttk.LabelFrame(self.images_frame, text="Imagen YIQ", padding=5)
        yiq_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.fig_yiq = Figure(figsize=(3.5, 3), dpi=100)
        self.ax_yiq = self.fig_yiq.add_subplot(111)
        self.canvas_yiq = FigureCanvasTkAgg(self.fig_yiq, master=yiq_panel)
        self.canvas_yiq.get_tk_widget().pack(side="top", fill="both", expand=True)

        self.toolbar_yiq = NavigationToolbar2Tk(self.canvas_yiq, yiq_panel)
        self.toolbar_yiq.update()
        self.label_yiq_info = ttk.Label(yiq_panel, text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.label_yiq_info.pack(pady=5)

        # --- Panel Modificada ---
        modified_panel = ttk.LabelFrame(self.images_frame, text="RGB Modificada", padding=5)
        modified_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.fig_modificada = Figure(figsize=(3.5, 3), dpi=100)
        self.ax_modificada = self.fig_modificada.add_subplot(111)
        self.canvas_modificada = FigureCanvasTkAgg(self.fig_modificada, master=modified_panel)
        self.canvas_modificada.get_tk_widget().pack(side="top", fill="both", expand=True)

        self.toolbar_modificada = NavigationToolbar2Tk(self.canvas_modificada, modified_panel)
        self.toolbar_modificada.update()
        self.label_modificada_info = ttk.Label(modified_panel, text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.label_modificada_info.pack(pady=5)

    # ---------------- Update display ----------------
    def _update_image_display(self):
        # Original
        self.ax_original.clear()
        if self.original_image_np is not None:
            self.ax_original.imshow(self.original_image_np)
            self.ax_original.set_title("Original")
            self.label_original_info.config(
                text=f"Dimensiones: {self.original_image_np.shape}\nTipo de Dato: {self.original_image_np.dtype}"
            )
        else:
            self.ax_original.text(0.5, 0.5, "No hay imagen", ha="center", va="center")
            self.label_original_info.config(text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.ax_original.axis("off")
        self.canvas_original.draw()
        

        # YIQ
        self.ax_yiq.clear()
        if self.yiq_image is not None:
         normalized_yiq = (self.yiq_image - self.yiq_image.min()) / (np.ptp(self.yiq_image) + 1e-8)
         self.ax_yiq.imshow(normalized_yiq)
         self.ax_yiq.set_title("YIQ")
        else:
         self.ax_yiq.text(0.5, 0.5, "No YIQ", ha="center", va="center")
         self.ax_yiq.axis("off")
         self.canvas_yiq.draw()
         self.canvas_yiq.flush_events() 


        # RGB Modificada
        self.ax_modificada.clear()
        if self.modified_image is not None:
            self.ax_modificada.imshow(self.modified_image)
            self.ax_modificada.set_title("RGB Modificada")
            self.label_modificada_info.config(
                text=f"Dimensiones: {self.modified_image.shape}\nTipo de Dato: {self.modified_image.dtype}"
            )
        else:
            self.ax_modificada.text(0.5, 0.5, "No RGB modificado", ha="center", va="center")
            self.label_modificada_info.config(text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.ax_modificada.axis("off")
        self.canvas_modificada.draw()   

    # ---------------- Funciones Workflow ----------------
    def mostrarYIQ(self):
        if self.image_np is None:
            messagebox.showwarning("Advertencia", "Cargue una imagen primero.")
            return
        self.yiq_image = self.rgb_to_yiq(self.image_np)
        self._update_image_display()

    def modYIQ(self):
        if self.image_np is None:
            messagebox.showwarning("Advertencia", "Cargue una imagen primero.")
            return
        try:
            a = float(self.entries[0].get())
            b = float(self.entries[1].get())
            self.modified_image = self.modify_image(self.image_np, a, b)
            self.yiq_image = self.rgb_to_yiq(self.modified_image)
            messagebox.showinfo("Éxito", "Imagen modificada correctamente")
            self._update_image_display()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_modified_rgb(self):
        if self.modified_image is not None:
            self._update_image_display()
        else:
            messagebox.showwarning("Advertencia", "Aplique la modificación primero.")

    # ---------------- Conversión ----------------
    def rgb_to_yiq(self, img):
        img_norm = img / 255.0
        T = np.array([[0.299, 0.587, 0.114],
                      [0.596, -0.274, -0.322],
                      [0.211, -0.523, 0.312]])
        yiq = img_norm @ T.T
        return yiq

    def modify_image(self, img, a, b):
        yiq = self.rgb_to_yiq(img)
        y, i, q = yiq[..., 0], yiq[..., 1], yiq[..., 2]

        y_mod = np.clip(a * y, 0, 1)
        i_mod = np.clip(b * i, -0.5957, 0.5957)
        q_mod = np.clip(b * q, -0.5226, 0.5226)

        yiq_mod = np.stack([y_mod, i_mod, q_mod], axis=-1)
        T_inv = np.array([[1, 0.956, 0.621],
                          [1, -0.272, -0.647],
                          [1, -1.106, 1.703]])
        rgb_mod = yiq_mod @ T_inv.T
        rgb_mod = np.clip(rgb_mod, 0, 1) * 255
        return rgb_mod.astype(np.uint8)
