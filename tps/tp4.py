import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import imageio.v3 as iio
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import os

# --- Añadir la raíz del proyecto al path ---
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.append(project_root)
    import my_functions as mf
except ImportError:
    messagebox.showerror("Error", "No se pudo importar 'my_functions.py'.")
    sys.exit(1)

try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
except ImportError:
    ttkb = None
    PRIMARY, INFO, SUCCESS, DANGER, LIGHT = "primary", "info", "success", "danger", "light"

class TP4Frame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.image_raw = None
        self.image_processed = None
        
        self.filter_var = tk.StringVar()

        self._create_widgets()
        self.update_image_displays()

    def _create_widgets(self):
        control_frame = ttk.LabelFrame(self, text="Controles de Filtrado", padding=15)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self._create_control_panel(control_frame)
        
        images_frame = ttk.Frame(self, padding=10)
        images_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self._create_image_panel(images_frame)

    def _create_control_panel(self, parent):
        btn_load = ttk.Button(parent, text="Cargar Imagen", command=self.load_image, bootstyle=PRIMARY)
        btn_load.pack(fill=tk.X, pady=(0, 10))
        
        btn_save = ttk.Button(parent, text="Guardar Imagen", command=self.save_image, bootstyle=(LIGHT, OUTLINE))
        btn_save.pack(fill=tk.X, pady=(0, 10))

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        ttk.Label(parent, text="Seleccionar Filtro:").pack(anchor=tk.W)
        
        filter_options = [
            "--- Pasabajos ---", "Plano 3x3", "Plano 5x5", "Plano 7x7",
            "Bartlett 3x3", "Bartlett 5x5", "Bartlett 7x7",
            "Gaussiano 5x5", "Gaussiano 7x7",
            "--- Detectores de Bordes ---", "Laplaciano v4", "Laplaciano v8",
            "Sobel N (Norte)", "Sobel NE (Noreste)", "Sobel E (Este)", "Sobel SE (Sudeste)",
            "Sobel S (Sur)", "Sobel SO (Sudoeste)", "Sobel O (Oeste)", "Sobel NO (Noroeste)",
            "--- Otros Filtros ---", "Pasaaltos (fc=0.2)", "Pasaaltos (fc=0.4)", "Pasabanda (DoG)"
        ]
        
        self.filter_combo = ttk.Combobox(parent, textvariable=self.filter_var, values=filter_options, state="readonly")
        self.filter_combo.pack(fill=tk.X, pady=5)
        self.filter_combo.current(1)
        self.filter_combo.bind("<<ComboboxSelected>>", self.on_filter_select)

        btn_apply = ttk.Button(parent, text="Aplicar Filtro", command=self.apply_filter, bootstyle=SUCCESS)
        btn_apply.pack(fill=tk.X, pady=10)
        
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        btn_exit = ttk.Button(parent, text="Salir", command=self.parent.destroy, bootstyle=DANGER)
        btn_exit.pack(fill=tk.X, pady=5)

    def on_filter_select(self, event):
        if "---" in self.filter_var.get():
            self.filter_combo.current(self.filter_combo.current() + 1)

    def _create_image_panel(self, parent):
        parent.rowconfigure(0, weight=1); parent.columnconfigure(0, weight=1); parent.columnconfigure(1, weight=1)
        original_frame = ttk.LabelFrame(parent, text="Imagen Original (Luminancia)", padding=5)
        original_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.fig_original = Figure(dpi=100); self.ax_original = self.fig_original.add_subplot(111)
        self.canvas_original = FigureCanvasTkAgg(self.fig_original, master=original_frame)
        self.canvas_original.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        processed_frame = ttk.LabelFrame(parent, text="Imagen Filtrada", padding=5)
        processed_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.fig_processed = Figure(dpi=100); self.ax_processed = self.fig_processed.add_subplot(111)
        self.canvas_processed = FigureCanvasTkAgg(self.fig_processed, master=processed_frame)
        self.canvas_processed.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos de Imagen", "*.png *.jpg *.jpeg *.bmp"), ("Todos", "*.*")])
        if not file_path: return
        try:
            self.image_raw = iio.imread(file_path)
            if self.image_raw.ndim == 3 and self.image_raw.shape[2] == 4: self.image_raw = self.image_raw[:, :, :3]
            self.image_processed = None
            self.update_image_displays()
        except Exception as e: messagebox.showerror("Error al cargar", str(e))

    def save_image(self):
        if self.image_processed is None:
            messagebox.showwarning("Sin imagen", "No hay imagen procesada para guardar.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")])
        if not file_path: return
        try:
            # Convertir la imagen de flotante [0,1] a uint8 [0,255]
            image_to_save = (np.clip(self.image_processed, 0, 1) * 255).astype(np.uint8)
            iio.imwrite(file_path, image_to_save)
            messagebox.showinfo("Guardado", f"Imagen guardada en:\n{file_path}")
        except Exception as e: messagebox.showerror("Error al guardar", str(e))

    def update_image_displays(self):
        def draw_image(ax, canvas, image, title):
            ax.clear()
            if image is not None: ax.imshow(image, cmap='gray', vmin=0, vmax=1)
            else: ax.text(0.5, 0.5, title, ha="center", va="center", fontsize=14, color="gray")
            ax.axis("off")
            canvas.draw()
        y_channel = None
        if self.image_raw is not None:
            if self.image_raw.ndim == 3: y_channel = mf.rgb2yiq(self.image_raw.astype(np.float32) / 255.0)[:, :, 0]
            else: y_channel = self.image_raw.astype(np.float32) / 255.0
        draw_image(self.ax_original, self.canvas_original, y_channel, "Cargar Imagen")
        draw_image(self.ax_processed, self.canvas_processed, self.image_processed, "Resultado")
    
    def apply_filter(self):
        if self.image_raw is None: messagebox.showwarning("Sin imagen", "Por favor, carga una imagen primero."); return
        if self.image_raw.ndim == 3: grayscale_image = mf.rgb2yiq(self.image_raw.astype(np.float32) / 255.0)[:, :, 0]
        else: grayscale_image = self.image_raw.astype(np.float32) / 255.0
        filter_name = self.filter_var.get()
        kernel = mf.get_kernel(filter_name)
        if kernel is None: messagebox.showerror("Error", f"Filtro '{filter_name}' no implementado."); return
        convolved_image = mf.convolve2d(grayscale_image, kernel)
        if "Sobel" in filter_name or "Laplaciano" in filter_name:
            max_val = np.max(np.abs(convolved_image))
            if max_val > 0: self.image_processed = (convolved_image / max_val * 0.5) + 0.5
            else: self.image_processed = np.full_like(convolved_image, 0.5)
        else: self.image_processed = np.clip(convolved_image, 0, 1)
        self.update_image_displays()

def main():
    if ttkb: root = ttkb.Window(themename="superhero")
    else: root = tk.Tk()
    root.title("Trabajo Práctico 4 - Filtrado por Convolución")
    root.geometry("1100x450")
    app_frame = TP4Frame(root)
    app_frame.pack(fill="both", expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()

