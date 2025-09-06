import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import tkinter as tk 
from tkinter import filedialog, messagebox, ttk
import numpy as np
import imageio.v3 as iio
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


class TPBaseFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.image_np = None
        self.original_image_np = None
        self.current_image_title = "Imagen Modificada"

        self._create_widgets()
        self._setup_matplotlib_canvases()
        self._update_image_display()

    #  Widgets básicos 
    def _create_widgets(self):
        # Panel lateral con botones base
        self.control_frame = ttk.Frame(self, padding=10)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Button(self.control_frame, text="Cargar Imagen", command=self.abrir_imagen).pack(fill=tk.X, pady=5)
        ttk.Button(self.control_frame, text="Guardar Imagen", command=self.guardar_imagen).pack(fill=tk.X, pady=5)
        ttk.Button(self.control_frame, text="Invertir Colores", command=self.invertir_colores).pack(fill=tk.X, pady=5)
        ttk.Button(self.control_frame, text="Mostrar Histograma", command=self.mostrar_histograma).pack(fill=tk.X, pady=5)
        ttk.Button(self.control_frame, text="Restaurar Original", command=self.restaurar_original).pack(fill=tk.X, pady=5)

    def _setup_matplotlib_canvases(self):
        self.images_frame = ttk.Frame(self)
        self.images_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        #  Panel Imagen Original 
        original_panel = ttk.LabelFrame(self.images_frame, text="Imagen Original", padding=5)
        original_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.fig_original = Figure(figsize=(4, 3), dpi=100)
        self.ax_original = self.fig_original.add_subplot(111)
        self.canvas_original = FigureCanvasTkAgg(self.fig_original, master=original_panel)
        self.canvas_original.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Toolbar para imagen original
        self.toolbar_original = NavigationToolbar2Tk(self.canvas_original, original_panel)
        self.toolbar_original.update()

        # Info de imagen original
        self.label_original_info = ttk.Label(original_panel, text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.label_original_info.pack(pady=5)

        # Panel Imagen Modificada 
        modified_panel = ttk.LabelFrame(self.images_frame, text="Imagen Modificada", padding=5)
        modified_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.fig_modificada = Figure(figsize=(4, 3), dpi=100)
        self.ax_modificada = self.fig_modificada.add_subplot(111)
        self.canvas_modificada = FigureCanvasTkAgg(self.fig_modificada, master=modified_panel)
        self.canvas_modificada.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Toolbar para imagen modificada
        self.toolbar_modificada = NavigationToolbar2Tk(self.canvas_modificada, modified_panel)
        self.toolbar_modificada.update()

        # Info de imagen modificada
        self.label_modificada_info = ttk.Label(modified_panel, text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.label_modificada_info.pack(pady=5)

    #  Funciones de actualización 
    def _update_image_display(self):
        # Imagen Original
        self.ax_original.clear()
        if self.original_image_np is not None:
            self.ax_original.imshow(self.original_image_np)
            self.ax_original.set_title("Imagen Original")
            self.label_original_info.config(
                text=f"Dimensiones: {self.original_image_np.shape}\nTipo de Dato: {self.original_image_np.dtype}"
            )
        else:
            self.ax_original.text(0.5, 0.5, "No hay imagen", ha='center', va='center')
            self.label_original_info.config(text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.ax_original.axis('off')
        self.canvas_original.draw()

        # Imagen Modificada
        self.ax_modificada.clear()
        if self.image_np is not None:
            self.ax_modificada.imshow(self.image_np)
            self.ax_modificada.set_title(self.current_image_title)
            self.label_modificada_info.config(
                text=f"Dimensiones: {self.image_np.shape}\nTipo de Dato: {self.image_np.dtype}"
            )
        else:
            self.ax_modificada.text(0.5, 0.5, "No hay imagen", ha='center', va='center')
            self.label_modificada_info.config(text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.ax_modificada.axis('off')
        self.canvas_modificada.draw()

    # Funciones comunes 
    def abrir_imagen(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos de Imagen", "*.png *.jpg *.jpeg"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            try:
                self.image_np = iio.imread(file_path)
                self.original_image_np = self.image_np.copy()
                self.current_image_title = "Imagen Cargada"
                self._update_image_display()
            except Exception as e:
                messagebox.showerror("Error al cargar imagen", str(e))

    def guardar_imagen(self):
        if self.image_np is None:
            messagebox.showwarning("Advertencia", "No hay imagen para guardar.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPG", "*.jpg"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            try:
                iio.imwrite(file_path, self.image_np)
            except Exception as e:
                messagebox.showerror("Error al guardar imagen", str(e))

    def invertir_colores(self):
        if self.image_np is None:
            return
        if self.image_np.ndim == 2:
            self.image_np = 255 - self.image_np
        elif self.image_np.shape[2] >= 3:
            self.image_np[:, :, :3] = 255 - self.image_np[:, :, :3]
        self.current_image_title = "Colores Invertidos"
        self._update_image_display()

    def mostrar_histograma(self):
        if self.image_np is None:
            messagebox.showwarning("Advertencia", "Cargue una imagen primero para mostrar el histograma.")
            return

        try:
            hist_window = tk.Toplevel(self)
            hist_window.title("Histograma de la Imagen")
            hist_window.geometry("800x600")

            fig_hist = Figure(figsize=(7, 5), dpi=100)
            ax_hist = fig_hist.add_subplot(111)

            if self.image_np.ndim == 2:
                ax_hist.hist(self.image_np.ravel(), bins=256, range=(0, 256), color='gray', alpha=0.7)
                ax_hist.set_title('Histograma de Escala de Grises')
                ax_hist.set_xlabel('Intensidad')
                ax_hist.set_ylabel('Frecuencia')
            elif self.image_np.shape[2] >= 3:
                colors = ('b', 'g', 'r')
                for i, col in enumerate(colors):
                    # Asegurarse de que el canal existe
                    if i < self.image_np.shape[2]:
                        ax_hist.hist(self.image_np[:, :, i].ravel(), bins=256, range=(0, 256), color=col, alpha=0.7, label=f'Canal {["Azul", "Verde", "Rojo"][i]}')
                ax_hist.set_title('Histograma de Canales de Color (RGB)')
                ax_hist.set_xlabel('Intensidad de Píxel')
                ax_hist.set_ylabel('Frecuencia')
                ax_hist.legend()
            else:
                messagebox.showerror("Error", "Formato de imagen no soportado para el histograma.")
                hist_window.destroy()
                return

            canvas_hist = FigureCanvasTkAgg(fig_hist, master=hist_window)
            canvas_hist_widget = canvas_hist.get_tk_widget()
            canvas_hist_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            toolbar_hist = NavigationToolbar2Tk(canvas_hist, hist_window)
            toolbar_hist.update()
            canvas_hist_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al mostrar el histograma: {e}")
            if 'hist_window' in locals() and hist_window.winfo_exists():
                hist_window.destroy()
    def restaurar_original(self):
        if self.original_image_np is not None:
            self.image_np = self.original_image_np.copy()
            self.current_image_title = "Imagen Restaurada"
            self._update_image_display()
