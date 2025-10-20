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
    PRIMARY, INFO, SUCCESS, DANGER, WARNING, LIGHT = "primary", "info", "success", "danger", "warning", "light"

class TP3Frame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent # Guardar referencia a la ventana principal para poder cerrarla
        self.image_raw = None
        self.image_processed = None
        
        self.filter_var = tk.StringVar(value="Filtro Raíz")
        self.ymin_var = tk.DoubleVar(value=0.2)
        self.ymax_var = tk.DoubleVar(value=0.8)

        self._create_widgets()
        self.update_graph()

    def _create_widgets(self):
        # --- Layout Principal: Paneles verticalmente ---
        top_controls_frame = ttk.Frame(self, padding=(10, 10, 10, 0))
        top_controls_frame.pack(fill=tk.X)
        self._create_top_control_panel(top_controls_frame)

        images_frame = ttk.Frame(self, padding=10)
        images_frame.pack(fill=tk.BOTH, expand=True)
        self._create_image_panel(images_frame)

    def _create_top_control_panel(self, parent):
        parent.columnconfigure(0, weight=1) # Columna para botones de acción
        parent.columnconfigure(1, weight=4) # Columna ancha para filtros
        
        action_frame = ttk.LabelFrame(parent, text="Acciones", padding=10)
        action_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        btn_load = ttk.Button(action_frame, text="Cargar Imagen", command=self.load_image, bootstyle=PRIMARY)
        btn_load.pack(fill=tk.X, pady=3)
        
        btn_apply = ttk.Button(action_frame, text="Aplicar Filtro", command=self.apply_filter, bootstyle=SUCCESS)
        btn_apply.pack(fill=tk.X, pady=3)
        
        btn_hist_orig = ttk.Button(action_frame, text="Hist. Original", command=self.show_original_histogram, bootstyle=INFO)
        btn_hist_orig.pack(fill=tk.X, pady=3)
        
        btn_hist_proc = ttk.Button(action_frame, text="Hist. Procesado", command=self.show_processed_histogram, bootstyle=WARNING)
        btn_hist_proc.pack(fill=tk.X, pady=3)
        
        ttk.Separator(action_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(10, 5))
        btn_exit = ttk.Button(action_frame, text="Salir", command=self.parent.destroy, bootstyle=DANGER)
        btn_exit.pack(fill=tk.X, pady=3)
        
        filter_controls_frame = ttk.LabelFrame(parent, text="Configuración de Filtro", padding=10)
        filter_controls_frame.grid(row=0, column=1, sticky="nsew")
        self._create_filter_controls(filter_controls_frame)

    def _create_filter_controls(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=2)
        
        radio_frame = ttk.Frame(parent)
        radio_frame.grid(row=0, column=0, sticky="nsw", padx=(0, 10))
        
        filters = ["Filtro Raíz", "Filtro Cuadrático", "Filtro Lineal a Trozos", "Ecualización de Histograma", "Normalización de Histograma"]
        for f in filters:
            rb = ttk.Radiobutton(radio_frame, text=f, variable=self.filter_var, value=f, command=self.update_graph)
            rb.pack(anchor=tk.W, pady=3)

        right_panel = ttk.Frame(parent)
        right_panel.grid(row=0, column=1, sticky="nsew")

        slider_frame = ttk.Frame(right_panel)
        slider_frame.pack(fill=tk.X)
        ttk.Label(slider_frame, text="Y Mínimo:").pack(anchor=tk.W)
        ttk.Scale(slider_frame, from_=0.0, to=1.0, variable=self.ymin_var, command=self.update_graph).pack(fill=tk.X, pady=(0, 5))
        ttk.Label(slider_frame, text="Y Máximo:").pack(anchor=tk.W)
        ttk.Scale(slider_frame, from_=0.0, to=1.0, variable=self.ymax_var, command=self.update_graph).pack(fill=tk.X)
        
        self.fig_graph = Figure(figsize=(3, 2.5), dpi=100)
        self.ax_graph = self.fig_graph.add_subplot(111)
        self.canvas_graph = FigureCanvasTkAgg(self.fig_graph, master=right_panel)
        self.canvas_graph.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=(10, 0))

    def _create_image_panel(self, parent):
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        original_frame = ttk.LabelFrame(parent, text="Imagen Original", padding=5)
        original_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.fig_original = Figure(dpi=100)
        self.ax_original = self.fig_original.add_subplot(111)
        self.canvas_original = FigureCanvasTkAgg(self.fig_original, master=original_frame)
        self.canvas_original.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        processed_frame = ttk.LabelFrame(parent, text="Imagen Procesada", padding=5)
        processed_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.fig_processed = Figure(dpi=100)
        self.ax_processed = self.fig_processed.add_subplot(111)
        self.canvas_processed = FigureCanvasTkAgg(self.fig_processed, master=processed_frame)
        self.canvas_processed.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.update_image_displays()

    def update_graph(self, *args):
        self.ax_graph.clear()
        x = np.linspace(0, 1, 256)
        filter_type = self.filter_var.get()
        
        adaptive_filters = ["Ecualización de Histograma", "Normalización de Histograma"]
        if filter_type in adaptive_filters:
            self.ax_graph.set_xticks([])
            self.ax_graph.set_yticks([])
            explanation = "Función adaptativa\n(depende de la imagen)"
            self.ax_graph.text(0.5, 0.5, explanation, ha="center", va="center", transform=self.ax_graph.transAxes)
        else:
            y = np.zeros_like(x)
            if filter_type == "Filtro Raíz": y = mf.filtro_raiz(x)
            elif filter_type == "Filtro Cuadrático": y = mf.filtro_cuadratico(x)
            elif filter_type == "Filtro Lineal a Trozos": y = mf.filtro_lineal_a_trozos(x, self.ymin_var.get(), self.ymax_var.get())
            
            plot_color = 'dodgerblue'
            self.ax_graph.plot(x, y, color=plot_color)
            self.ax_graph.set_title(filter_type, fontsize=10)
            self.ax_graph.set_xlabel("Entrada", fontsize=8)
            self.ax_graph.set_ylabel("Salida", fontsize=8)
            self.ax_graph.set_xlim(0, 1)
            self.ax_graph.set_ylim(0, 1)
            self.ax_graph.grid(True, linestyle='--', alpha=0.6)
        
        self.fig_graph.tight_layout(pad=0.5)
        self.canvas_graph.draw()
    
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos de Imagen", "*.png *.jpg *.jpeg *.bmp"), ("Todos", "*.*")])
        if not file_path: return
        try:
            self.image_raw = iio.imread(file_path)
            if self.image_raw.ndim == 3 and self.image_raw.shape[2] == 4:
                self.image_raw = self.image_raw[:, :, :3]
            self.image_processed = None
            self.update_image_displays()
        except Exception as e:
            messagebox.showerror("Error al cargar", str(e))

    def update_image_displays(self):
        def draw_image(ax, canvas, image, title):
            ax.clear()
            if image is not None:
                ax.imshow(image)
            else:
                ax.text(0.5, 0.5, title, ha="center", va="center", fontsize=14, color="gray")
            ax.axis("off")
            canvas.draw()
        
        draw_image(self.ax_original, self.canvas_original, self.image_raw, "Cargar Imagen")
        draw_image(self.ax_processed, self.canvas_processed, self.image_processed, "Resultado")

    def apply_filter(self):
        if self.image_raw is None:
            messagebox.showwarning("Sin imagen", "Por favor, carga una imagen primero.")
            return

        img_float = self.image_raw.astype(np.float32) / 255.0
        img_yiq = mf.rgb2yiq(img_float)
        y_channel = img_yiq[:, :, 0]

        filters_map = {
            "Filtro Raíz": mf.filtro_raiz,
            "Filtro Cuadrático": mf.filtro_cuadratico,
            "Filtro Lineal a Trozos": lambda y: mf.filtro_lineal_a_trozos(y, self.ymin_var.get(), self.ymax_var.get()),
            "Ecualización de Histograma": mf.ecualizacion_histograma,
            "Normalización de Histograma": mf.normalizacion_histograma
        }
        
        process_function = filters_map.get(self.filter_var.get())
        if not process_function: return

        y_new = process_function(y_channel)
        
        img_yiq_processed = img_yiq.copy()
        img_yiq_processed[:, :, 0] = y_new
        img_rgb_processed_float = mf.yiq2rgb(img_yiq_processed)
        self.image_processed = (np.clip(img_rgb_processed_float, 0, 1) * 255).astype(np.uint8)

        self.update_image_displays()

    def _show_histogram_for_image(self, image_data, title, y_max_limit=None):
        if image_data is None:
            messagebox.showwarning("Sin imagen", f"No hay imagen para generar el '{title}'.")
            return

        hist_window = tk.Toplevel(self)
        hist_window.title(f"Histograma de Luminancia - {title}")
        
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        img_float = image_data.astype(np.float32) / 255.0
        y_channel = mf.rgb2yiq(img_float)[:, :, 0]
        
        counts, bins = np.histogram(y_channel.flatten(), bins=50, range=(0, 1))
        counts = counts / counts.sum() * 100
        
        bar_color = 'dodgerblue'
        ax.bar(bins[:-1], counts, width=np.diff(bins)[0], align='edge', color=bar_color)
        
        ax.set_title(f"Distribución de Luminancia ({title})")
        ax.set_xlabel("Luminancia (Y)")
        ax.set_ylabel("Frecuencia Relativa (%)")
        ax.set_xlim(0, 1)
        
        if y_max_limit:
            ax.set_ylim(0, y_max_limit)

        canvas = FigureCanvasTkAgg(fig, master=hist_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_original_histogram(self):
        # AJUSTE: Usar el límite fijo de 35
        self._show_histogram_for_image(self.image_raw, "Original", y_max_limit=35)

    def show_processed_histogram(self):
        # AJUSTE: Usar el límite fijo de 35
        self._show_histogram_for_image(self.image_processed, "Procesada", y_max_limit=35)


def main():
    if ttkb:
        root = ttkb.Window(themename="superhero")
    else:
        root = tk.Tk()
    
    root.title("Trabajo Práctico 3 - Manipulación de Luminancia")
    # AJUSTE: Cambiar tamaño de la ventana a 800x800
    root.geometry("800x800")
    
    app_frame = TP3Frame(root)
    app_frame.pack(fill="both", expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()

