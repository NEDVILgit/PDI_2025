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
    PRIMARY, INFO, SUCCESS, DANGER, LIGHT, SECONDARY = "primary", "info", "success", "danger", "light", "secondary"

class TP5Frame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.image_original = None # Imagen para el panel izquierdo
        self.image_processed = None # Imagen para el panel derecho
        self.filter_var = tk.StringVar()
        self._create_widgets()
        self.update_image_displays()

    def _create_widgets(self):
        # --- Layout Principal: Dos paneles de imagen y un panel de control en medio ---
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1, minsize=180) # Panel de control con ancho fijo
        self.columnconfigure(2, weight=2)
        self.rowconfigure(0, weight=1)

        # --- Paneles de Imagen ---
        self._create_image_panel(self, 0, "Imagen Original")
        self._create_image_panel(self, 2, "Imagen Procesada")

        # --- Panel de Control ---
        control_frame = ttk.LabelFrame(self, text="Controles", padding=15)
        control_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self._create_control_panel(control_frame)

    def _create_image_panel(self, parent, col, title):
        frame = ttk.LabelFrame(parent, text=title, padding=5)
        frame.grid(row=0, column=col, sticky="nsew", padx=5, pady=5)
        
        fig = Figure(dpi=100)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        if col == 0:
            self.fig_original, self.ax_original, self.canvas_original = fig, ax, canvas
        else:
            self.fig_processed, self.ax_processed, self.canvas_processed = fig, ax, canvas

    def _create_control_panel(self, parent):
        parent.pack_propagate(False) # Evita que el frame se encoja
        
        btn_load = ttk.Button(parent, text="Cargar Imagen", command=self.load_image, bootstyle=PRIMARY)
        btn_load.pack(fill=tk.X, pady=5, padx=5)

        ttk.Separator(parent).pack(fill=tk.X, pady=10, padx=5)
        
        filter_options = ["Erosión 3x3", "Dilatación 3x3", "Apertura 3x3", "Cierre 3x3", "Borde Morfológico 3x3", "Mediana 3x3"]
        self.filter_combo = ttk.Combobox(parent, textvariable=self.filter_var, values=filter_options, state="readonly")
        self.filter_combo.pack(fill=tk.X, pady=5, padx=5)
        self.filter_combo.current(0)

        btn_apply = ttk.Button(parent, text="Filtrar ->", command=self.apply_filter, bootstyle=SUCCESS)
        btn_apply.pack(fill=tk.X, pady=5, padx=5)
        
        btn_copy = ttk.Button(parent, text="<- Copiar", command=self.copy_to_original, bootstyle=SECONDARY)
        btn_copy.pack(fill=tk.X, pady=5, padx=5)

        # Espaciador para empujar los botones de abajo hacia abajo
        ttk.Frame(parent).pack(fill=tk.Y, expand=True)

        btn_save = ttk.Button(parent, text="Guardar Imagen", command=self.save_image, bootstyle=(LIGHT, OUTLINE))
        btn_save.pack(side=tk.BOTTOM, fill=tk.X, pady=5, padx=5)

        btn_exit = ttk.Button(parent, text="Salir", command=self.parent.destroy, bootstyle=DANGER)
        btn_exit.pack(side=tk.BOTTOM, fill=tk.X, pady=5, padx=5)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos de Imagen", "*.png *.jpg *.jpeg *.bmp"), ("Todos", "*.*")])
        if not file_path: return
        try:
            raw_image = iio.imread(file_path)
            # Convertir a flotante y manejar canal alfa si existe
            if raw_image.ndim == 3 and raw_image.shape[2] == 4:
                raw_image = raw_image[:, :, :3]
            self.image_original = raw_image.astype(np.float32) / 255.0
                
            self.image_processed = None
            self.update_image_displays()
        except Exception as e: messagebox.showerror("Error al cargar", str(e))

    def copy_to_original(self):
        if self.image_processed is None:
            messagebox.showwarning("Sin imagen", "No hay imagen procesada para copiar.")
            return
        self.image_original = self.image_processed.copy()
        self.image_processed = None
        self.update_image_displays()

    def apply_filter(self):
        if self.image_original is None:
            messagebox.showwarning("Sin imagen", "Por favor, carga una imagen primero."); return
        
        filter_name = self.filter_var.get()
        # El tamaño del elemento estructurante es 3x3 para todos
        structure_size = 3
        
        operations = {
            "Erosión 3x3": mf.erosion,
            "Dilatación 3x3": mf.dilatacion,
            "Apertura 3x3": mf.apertura,
            "Cierre 3x3": mf.cierre,
            "Borde Morfológico 3x3": mf.borde_morfologico,
            "Mediana 3x3": mf.mediana,
        }
        
        operation_func = operations.get(filter_name)
        if operation_func:
            self.image_processed = operation_func(self.image_original, structure_size)
            self.update_image_displays()
        else:
            messagebox.showerror("Error", f"Filtro '{filter_name}' no implementado.")

    def save_image(self):
        if self.image_processed is None:
            messagebox.showwarning("Sin imagen", "No hay imagen procesada para guardar."); return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
        if not file_path: return
        try:
            image_to_save = (np.clip(self.image_processed, 0, 1) * 255).astype(np.uint8)
            iio.imwrite(file_path, image_to_save)
            messagebox.showinfo("Guardado", f"Imagen guardada en:\n{file_path}")
        except Exception as e: messagebox.showerror("Error al guardar", str(e))

    def update_image_displays(self):
        def draw_image(ax, canvas, image, title):
            ax.clear()
            if image is not None:
                # Determinar si la imagen es a color o escala de grises
                if image.ndim == 3:
                    ax.imshow(image) # Muestra imagen a color
                else:
                    ax.imshow(image, cmap='gray', vmin=0, vmax=1) # Muestra en escala de grises
            else:
                ax.text(0.5, 0.5, title, ha="center", va="center", fontsize=14, color="gray")
            ax.axis("off")
            canvas.draw()
            
        draw_image(self.ax_original, self.canvas_original, self.image_original, "Cargar Imagen")
        draw_image(self.ax_processed, self.canvas_processed, self.image_processed, "Resultado")

def main():
    if ttkb: root = ttkb.Window(themename="superhero")
    else: root = tk.Tk()
    root.title("Trabajo Práctico 5 - Morfología Matemática")
    root.geometry("1000x500")
    app_frame = TP5Frame(root)
    app_frame.pack(fill="both", expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()
