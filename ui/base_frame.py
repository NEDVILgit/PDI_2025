import tkinter as tk
from tkinter import Image, filedialog, messagebox, ttk
import imageio.v3 as iio
from matplotlib import image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np


class TPBaseFrame(ttk.Frame):
    """Clase base avanzada para todos los TPs. Incluye carga, guardado, edición de píxeles, inversión e histograma."""

    def __init__(self, parent):
        super().__init__(parent, padding="10")
        self.control_frame = ttk.Frame(self)
        self.control_frame.pack(side="left", fill="y", padx=5, pady=5)

        #Frame para mostrar la imagen
        self.image_label = ttk.Label(self)
        self.image_label.pack(side="right", expand=True)

        #crear los widgets
        self._create_widgets()
        self.image_np = None
        self.original_image_np = None
        self.fig = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self._setup_matplotlib_canvas()

    def _create_widgets(self):
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Botones de archivo
        ttk.Button(control_frame, text="Abrir Imagen", command=self.abrir_imagen_desde_archivo).pack(pady=5, fill=tk.X)
        ttk.Button(control_frame, text="Guardar Imagen", command=self.guardar_imagen_a_archivo).pack(pady=5, fill=tk.X)

        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

        
        # Botones de efectos
        ttk.Button(control_frame, text="Invertir Colores", command=self.invertir_colores).pack(pady=5, fill=tk.X)
        ttk.Button(control_frame, text="Mostrar Histograma", command=self.mostrar_histograma).pack(pady=5, fill=tk.X)

        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

        ttk.Button(control_frame, text="Restaurar Imagen Original", command=self._restore_original_image).pack(pady=5, fill=tk.X)

    def _setup_matplotlib_canvas(self):
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.canvas_frame)
        self.toolbar.update()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _update_image_display(self, image_np=None):
      self.ax.clear()
    
      # Usar la imagen pasada como argumento o la predeterminada
      img_to_show = image_np if image_np is not None else self.image_np

      if img_to_show is not None:
          self.ax.imshow(img_to_show)
      else:
        self.ax.text(0.5, 0.5, "No hay imagen cargada",
                     horizontalalignment='center',
                     verticalalignment='center',
                     transform=self.ax.transAxes, fontsize=16)
    
      self.ax.axis('off')
      self.canvas.draw()


    def abrir_imagen_desde_archivo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg"), ("Todos los archivos", "*.*")])
        if file_path:
            try:
                self.image_np = iio.imread(file_path)
                self.original_image_np = self.image_np.copy()
                self._update_image_display()
                messagebox.showinfo("Éxito", "Imagen cargada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")

    def guardar_imagen_a_archivo(self):
        if self.image_np is None:
            messagebox.showwarning("Advertencia", "No hay imagen para guardar.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG", "*.png"), ("JPG", "*.jpg")])
        if file_path:
            try:
                iio.imwrite(file_path, self.image_np)
                messagebox.showinfo("Éxito", "Imagen guardada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la imagen: {e}")

    
    def invertir_colores(self):
        if self.image_np is None:
            messagebox.showwarning("Advertencia", "Cargue una imagen primero.")
            return
        if self.image_np.ndim == 2:
            self.image_np = 255 - self.image_np
        elif self.image_np.shape[2] >= 3:
            self.image_np[:, :, :3] = 255 - self.image_np[:, :, :3]
        self._update_image_display()

    def mostrar_histograma(self):
        if self.image_np is None:
            messagebox.showwarning("Advertencia", "Cargue una imagen primero.")
            return
        hist_window = tk.Toplevel(self)
        hist_window.title("Histograma")
        fig_hist = Figure(figsize=(6, 4), dpi=100)
        ax_hist = fig_hist.add_subplot(111)

        if self.image_np.ndim == 2:
            ax_hist.hist(self.image_np.ravel(), bins=256, range=(0, 256), color='gray', alpha=0.7)
        elif self.image_np.shape[2] >= 3:
            colors = ('r', 'g', 'b')
            for i, col in enumerate(colors):
                ax_hist.hist(self.image_np[:, :, i].ravel(), bins=256, range=(0, 256),
                             color=col, alpha=0.5, label=f"Canal {col.upper()}")
            ax_hist.legend()

        canvas_hist = FigureCanvasTkAgg(fig_hist, master=hist_window)
        canvas_hist.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        NavigationToolbar2Tk(canvas_hist, hist_window)

    def _restore_original_image(self):
        if self.original_image_np is None:
            return
        self.image_np = self.original_image_np.copy()
        self._update_image_display()
