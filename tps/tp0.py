import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import numpy as np
import imageio.v3 as iio
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Procesador de Imágenes Avanzado")
        self.root.geometry("1400x650") # Ajustado para más espacio

        self.image_np = None  # Almacenará la imagen como array de numpy
        self.original_image_np = None # Para reiniciar si es necesario
        self.current_image_title = "Imagen Modificada" # Título para la imagen actual

        # Configuración para mostrar la imagen original y la modificada
        self.fig_original = Figure(figsize=(4, 3), dpi=100) # Más pequeño
        self.ax_original = self.fig_original.add_subplot(111)

        self.fig_modified = Figure(figsize=(4, 3), dpi=100) # Más pequeño
        self.ax_modified = self.fig_modified.add_subplot(111)

        self._create_widgets()
        self._setup_matplotlib_canvases()

        self._update_image_display() # Mostrar estado inicial

    def _create_widgets(self):
        # Frame principal para los controles
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Botones de archivo
        ttk.Button(control_frame, text="Abrir Imagen", command=self.abrir_imagen_desde_archivo).pack(pady=5, fill=tk.X)
        ttk.Button(control_frame, text="Guardar Imagen", command=self.guardar_imagen_a_archivo).pack(pady=5, fill=tk.X)
        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

        # Controles de manipulación de píxeles
        pixel_frame = ttk.LabelFrame(control_frame, text="Modificar Píxel", padding="10")
        pixel_frame.pack(pady=10, fill=tk.X)

        ttk.Label(pixel_frame, text="X:").grid(row=0, column=0, sticky="w", pady=2)
        self.x_entry = ttk.Entry(pixel_frame)
        self.x_entry.grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(pixel_frame, text="Y:").grid(row=1, column=0, sticky="w", pady=2)
        self.y_entry = ttk.Entry(pixel_frame)
        self.y_entry.grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(pixel_frame, text="R (0-255):").grid(row=2, column=0, sticky="w", pady=2)
        self.r_entry = ttk.Entry(pixel_frame)
        self.r_entry.grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Label(pixel_frame, text="G (0-255):").grid(row=3, column=0, sticky="w", pady=2)
        self.g_entry = ttk.Entry(pixel_frame)
        self.g_entry.grid(row=3, column=1, sticky="ew", pady=2)

        ttk.Label(pixel_frame, text="B (0-255):").grid(row=4, column=0, sticky="w", pady=2)
        self.b_entry = ttk.Entry(pixel_frame)
        self.b_entry.grid(row=4, column=1, sticky="ew", pady=2)

        ttk.Button(pixel_frame, text="Aplicar Píxel", command=self._apply_pixel_modification).grid(row=5, columnspan=2, pady=5, sticky="ew")
        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

        # Botones de efectos
        ttk.Button(control_frame, text="Invertir Colores", command=self.invertir_colores).pack(pady=5, fill=tk.X)
        ttk.Button(control_frame, text="Mostrar Histograma", command=self.mostrar_histograma).pack(pady=5, fill=tk.X)
        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

        # Reset button
        ttk.Button(control_frame, text="Restaurar Imagen Original", command=self._restore_original_image).pack(pady=5, fill=tk.X)

    def _setup_matplotlib_canvases(self):
        # Frame para las imágenes (original y modificada)
        images_frame = ttk.Frame(self.root)
        images_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Canvas para la imagen Original ---
        original_image_panel = ttk.LabelFrame(images_frame, text="Imagen Original", padding="5")
        original_image_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas_original = FigureCanvasTkAgg(self.fig_original, master=original_image_panel)
        self.canvas_widget_original = self.canvas_original.get_tk_widget()
        self.canvas_widget_original.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.label_original_info = ttk.Label(original_image_panel, text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.label_original_info.pack(pady=5)

        # Toolbar para la imagen original
        self.toolbar_original = NavigationToolbar2Tk(self.canvas_original, original_image_panel)
        self.toolbar_original.update()


        # --- Canvas para la imagen Modificada ---
        modified_image_panel = ttk.LabelFrame(images_frame, text="Imagen Modificada", padding="5")
        modified_image_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas_modified = FigureCanvasTkAgg(self.fig_modified, master=modified_image_panel)
        self.canvas_widget_modified = self.canvas_modified.get_tk_widget()
        self.canvas_widget_modified.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.label_modified_info = ttk.Label(modified_image_panel, text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.label_modified_info.pack(pady=5)

        # Toolbar para la imagen modificada
        self.toolbar_modified = NavigationToolbar2Tk(self.canvas_modified, modified_image_panel)
        self.toolbar_modified.update()

    def _update_image_display(self):
        # Actualizar imagen Original
        self.ax_original.clear()
        if self.original_image_np is not None:
            self.ax_original.imshow(self.original_image_np)
            self.ax_original.set_title("Original")
            shape_info = f"Ancho: {self.original_image_np.shape[1]}, Alto: {self.original_image_np.shape[0]}"
            channels_info = f", Canales: {self.original_image_np.shape[2]}" if self.original_image_np.ndim == 3 else ""
            dtype_info = f"Tipo de Dato: {self.original_image_np.dtype}"
            self.label_original_info.config(text=f"Dimensiones: {shape_info}{channels_info}\n{dtype_info}")
        else:
            self.ax_original.text(0.5, 0.5, "No hay imagen original", horizontalalignment='center', verticalalignment='center', transform=self.ax_original.transAxes, fontsize=12)
            self.label_original_info.config(text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.ax_original.axis('off')
        self.canvas_original.draw()

        # Actualizar imagen Modificada
        self.ax_modified.clear()
        if self.image_np is not None:
            self.ax_modified.imshow(self.image_np)
            self.ax_modified.set_title(self.current_image_title)
            shape_info = f"Ancho: {self.image_np.shape[1]}, Alto: {self.image_np.shape[0]}"
            channels_info = f", Canales: {self.image_np.shape[2]}" if self.image_np.ndim == 3 else ""
            dtype_info = f"Tipo de Dato: {self.image_np.dtype}"
            self.label_modified_info.config(text=f"Dimensiones: {shape_info}{channels_info}\n{dtype_info}")
        else:
            self.ax_modified.text(0.5, 0.5, "No hay imagen modificada", horizontalalignment='center', verticalalignment='center', transform=self.ax_modified.transAxes, fontsize=12)
            self.label_modified_info.config(text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.ax_modified.axis('off')
        self.canvas_modified.draw()

    def abrir_imagen_desde_archivo(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos de Imagen", "*.png *.jpg *.jpeg"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            try:
                self.image_np = iio.imread(file_path)
                self.original_image_np = self.image_np.copy()
                self.current_image_title = "Imagen Cargada" # Restablecer el título al cargar
                self._update_image_display()
            except Exception as e:
                messagebox.showerror("Error al cargar imagen", f"No se pudo cargar la imagen: {e}")

    def guardar_imagen_a_archivo(self):
        if self.image_np is None:
            messagebox.showwarning("Advertencia", "No hay ninguna imagen para guardar.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPG", "*.jpg"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            try:
                iio.imwrite(file_path, self.image_np)
            except Exception as e:
                messagebox.showerror("Error al guardar imagen", f"No se pudo guardar la imagen: {e}")

    def modificar_pixel(self, x, y, r, g, b):
        if self.image_np is None:
            messagebox.showwarning("Advertencia", "Cargue una imagen primero para modificar píxeles.")
            return

        try:
            x, y = int(x), int(y)
            r, g, b = int(r), int(g), int(b)

            if not (0 <= x < self.image_np.shape[1] and 0 <= y < self.image_np.shape[0]):
                messagebox.showerror("Error de Coordenadas", "Coordenadas fuera de los límites de la imagen.")
                return
            if not all(0 <= val <= 255 for val in [r, g, b]):
                messagebox.showerror("Error de Color", "Los valores de color (R, G, B) deben estar entre 0 y 255.")
                return

            if self.image_np.ndim == 2: # Imagen en escala de grises
                self.image_np = np.stack([self.image_np]*3, axis=-1)
            elif self.image_np.shape[2] == 4: # Imagen con canal alfa
                self.image_np = self.image_np[:, :, :3]

            self.image_np[y, x] = [r, g, b]
            self.current_image_title = f"Píxel en ({x},{y}) Modificado"
            self._update_image_display()

        except ValueError:
            messagebox.showerror("Error de Entrada", "Por favor, ingrese números válidos para las coordenadas y colores.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al modificar el píxel: {e}")

    def _apply_pixel_modification(self):
        x = self.x_entry.get()
        y = self.y_entry.get()
        r = self.r_entry.get()
        g = self.g_entry.get()
        b = self.b_entry.get()
        self.modificar_pixel(x, y, r, g, b)

    def invertir_colores(self):
        if self.image_np is None:
            messagebox.showwarning("Advertencia", "Cargue una imagen primero para invertir colores.")
            return

        try:
            if self.image_np.ndim == 2:
                self.image_np = 255 - self.image_np
            elif self.image_np.shape[2] >= 3:
                self.image_np[:, :, :3] = 255 - self.image_np[:, :, :3]
            else:
                messagebox.showerror("Error", "Formato de imagen no soportado para inversión de color.")
                return

            self.current_image_title = "Colores Invertidos"
            self._update_image_display()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al invertir los colores: {e}")

    def mostrar_histograma(self):
        if self.image_np is None:
            messagebox.showwarning("Advertencia", "Cargue una imagen primero para mostrar el histograma.")
            return

        try:
            hist_window = tk.Toplevel(self.root)
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

    def _restore_original_image(self):
        if self.original_image_np is None:
            messagebox.showwarning("Advertencia", "No hay una imagen original para restaurar.")
            return
        self.image_np = self.original_image_np.copy()
        self.current_image_title = "Restaurada a Original"
        self._update_image_display()


# Para ejecutar en Jupyter Lab dentro de VS Code o como script independiente:
if __name__ == "__main__":
    try:
        import ttkbootstrap as ttkb
        root = ttkb.Window(themename="superhero")
    except ImportError:
        print("ttkbootstrap no encontrado. Usando Tkinter estándar.")
        root = tk.Tk()

    app = ImageProcessorApp(root)
    root.mainloop()