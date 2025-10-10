import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import numpy as np
import imageio.v3 as iio
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from numpy.linalg import inv

# =======================
# Patrón Strategy
# =======================

class EstrategiaProcesamiento:
    def aplicar(self, imagen, *args, **kwargs):
        raise NotImplementedError("Debe implementar el método aplicar()")


class AjusteYIQ(EstrategiaProcesamiento):
    def __init__(self, a=1.0, b=1.0, rgb_to_yiq=None, yiq_to_rgb=None):
        self.a = a
        self.b = b
        self.rgb_to_yiq = rgb_to_yiq
        self.yiq_to_rgb = yiq_to_rgb

    def aplicar(self, imagen, *args, **kwargs):
        rgb_norm = imagen.astype(np.float64) / 255.0
        yiq = rgb_norm @ self.rgb_to_yiq.T

        yiq[:, :, 0] *= self.a
        yiq[:, :, 1] *= self.b
        yiq[:, :, 2] *= self.b

        yiq[:, :, 0] = np.clip(yiq[:, :, 0], 0.0, 1.0)
        yiq[:, :, 1] = np.clip(yiq[:, :, 1], -0.5957 + 1e-6, 0.5957 - 1e-6)
        yiq[:, :, 2] = np.clip(yiq[:, :, 2], -0.5226 + 1e-6, 0.5226 - 1e-6)

        rgb_norm_new = yiq @ self.yiq_to_rgb.T
        rgb_norm_new = np.clip(rgb_norm_new, 0.0, 1.0)
        return (rgb_norm_new * 255).astype(np.uint8)


class RestaurarOriginal(EstrategiaProcesamiento):
    def __init__(self, original):
        self.original = original

    def aplicar(self, imagen, *args, **kwargs):
        return self.original.copy()


# Contexto
class ProcesadorImagen:
    def __init__(self, estrategia: EstrategiaProcesamiento = None):
        self.estrategia = estrategia

    def set_estrategia(self, estrategia: EstrategiaProcesamiento):
        self.estrategia = estrategia

    def procesar(self, imagen, *args, **kwargs):
        if not self.estrategia:
            raise ValueError("No se ha definido una estrategia de procesamiento")
        return self.estrategia.aplicar(imagen, *args, **kwargs)


# =======================
# GUI
# =======================

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Procesador de Imágenes Avanzado con Strategy")
        self.root.geometry("1400x600")

        self.image_np = None
        self.original_image_np = None
        self.adjusted_vis = None

        self.a_value = 1.0
        self.b_value = 1.0
        self.a_var = tk.StringVar(value=f"{self.a_value:.2f}")
        self.b_var = tk.StringVar(value=f"{self.b_value:.2f}")

        # Matrices de conversión
        self.rgb_to_yiq = np.array([
            [0.299, 0.587, 0.114],
            [0.595716, -0.274453, -0.321263],
            [0.211456, -0.522591, 0.311135]
        ])
        self.yiq_to_rgb = inv(self.rgb_to_yiq)

        # Contexto
        self.procesador = ProcesadorImagen()

        # Configuración de las figuras
        self.fig_original = Figure(figsize=(4, 3), dpi=100)
        self.ax_original = self.fig_original.add_subplot(111)

        self.fig_adjusted = Figure(figsize=(4, 3), dpi=100)
        self.ax_adjusted = self.fig_adjusted.add_subplot(111)

        self._create_widgets()
        self._setup_matplotlib_canvases()
        self._update_image_display()

    # ---------------------
    # Widgets
    # ---------------------
    def _create_widgets(self):
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Button(control_frame, text="Abrir Imagen", command=self.abrir_imagen_desde_archivo).pack(pady=5, fill=tk.X)
        ttk.Button(control_frame, text="Guardar Imagen", command=self.guardar_imagen_a_archivo).pack(pady=5, fill=tk.X)
        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

        yiq_frame = ttk.LabelFrame(control_frame, text="Ajuste YIQ", padding="10")
        yiq_frame.pack(pady=10, fill=tk.X)

        ttk.Label(yiq_frame, text="Luminancia (a):").grid(row=0, column=0, sticky="w", pady=2)
        self.a_scale = ttk.Scale(yiq_frame, from_=0.1, to=2.0, orient=tk.HORIZONTAL, value=1.0, command=self._update_adjusted)
        self.a_scale.grid(row=0, column=1, sticky="ew", pady=2)
        self.a_entry = ttk.Entry(yiq_frame, textvariable=self.a_var, width=5)
        self.a_entry.grid(row=0, column=2, sticky="w", pady=2)
        self.a_entry.bind("<FocusOut>", self._update_a_from_entry)

        ttk.Label(yiq_frame, text="Saturación (b):").grid(row=1, column=0, sticky="w", pady=2)
        self.b_scale = ttk.Scale(yiq_frame, from_=0.1, to=2.0, orient=tk.HORIZONTAL, value=1.0, command=self._update_adjusted)
        self.b_scale.grid(row=1, column=1, sticky="ew", pady=2)
        self.b_entry = ttk.Entry(yiq_frame, textvariable=self.b_var, width=5)
        self.b_entry.grid(row=1, column=2, sticky="w", pady=2)
        self.b_entry.bind("<FocusOut>", self._update_b_from_entry)

        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

        ttk.Button(control_frame, text="Mostrar Histograma", command=self.mostrar_histograma).pack(pady=5, fill=tk.X)
        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

        ttk.Button(control_frame, text="Restaurar Imagen Original", command=self._restore_original_image).pack(pady=5, fill=tk.X)

    def _setup_matplotlib_canvases(self):
        images_frame = ttk.Frame(self.root)
        images_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Original
        original_image_panel = ttk.LabelFrame(images_frame, text="Imagen Original RGB", padding="5")
        original_image_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas_original = FigureCanvasTkAgg(self.fig_original, master=original_image_panel)
        self.canvas_widget_original = self.canvas_original.get_tk_widget()
        self.canvas_widget_original.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.label_original_info = ttk.Label(original_image_panel, text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.label_original_info.pack(pady=5)

        self.toolbar_original = NavigationToolbar2Tk(self.canvas_original, original_image_panel)
        self.toolbar_original.update()

        # Ajustada
        adjusted_image_panel = ttk.LabelFrame(images_frame, text="Imagen Ajustada YIQ", padding="5")
        adjusted_image_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas_adjusted = FigureCanvasTkAgg(self.fig_adjusted, master=adjusted_image_panel)
        self.canvas_widget_adjusted = self.canvas_adjusted.get_tk_widget()
        self.canvas_widget_adjusted.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.label_adjusted_info = ttk.Label(adjusted_image_panel, text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.label_adjusted_info.pack(pady=5)

        self.toolbar_adjusted = NavigationToolbar2Tk(self.canvas_adjusted, adjusted_image_panel)
        self.toolbar_adjusted.update()

    # ---------------------
    # Lógica GUI
    # ---------------------
    def _update_image_display(self):
        self.ax_original.clear()
        if self.original_image_np is not None:
            self.ax_original.imshow(self.original_image_np)
            self.ax_original.set_title("Original RGB")
            shape_info = f"Ancho: {self.original_image_np.shape[1]}, Alto: {self.original_image_np.shape[0]}"
            channels_info = f", Canales: {self.original_image_np.shape[2]}" if self.original_image_np.ndim == 3 else ""
            dtype_info = f"Tipo de Dato: {self.original_image_np.dtype}"
            self.label_original_info.config(text=f"Dimensiones: {shape_info}{channels_info}\n{dtype_info}")
        else:
            self.ax_original.text(0.5, 0.5, "No hay imagen original", ha='center', va='center', transform=self.ax_original.transAxes, fontsize=12)
            self.label_original_info.config(text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.ax_original.axis('off')
        self.canvas_original.draw()

        self.ax_adjusted.clear()
        if self.adjusted_vis is not None:
            self.ax_adjusted.imshow(self.adjusted_vis)
            self.ax_adjusted.set_title(f"Ajuste YIQ (a={self.a_value:.2f}, b={self.b_value:.2f})")
            shape_info = f"Ancho: {self.adjusted_vis.shape[1]}, Alto: {self.adjusted_vis.shape[0]}"
            channels_info = f", Canales: {self.adjusted_vis.shape[2]}" if self.adjusted_vis.ndim == 3 else ""
            dtype_info = f"Tipo de Dato: {self.adjusted_vis.dtype}"
            self.label_adjusted_info.config(text=f"Dimensiones: {shape_info}{channels_info}\n{dtype_info}")
        else:
            self.ax_adjusted.text(0.5, 0.5, "No hay imagen ajustada", ha='center', va='center', transform=self.ax_adjusted.transAxes, fontsize=12)
            self.label_adjusted_info.config(text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.ax_adjusted.axis('off')
        self.canvas_adjusted.draw()

    def abrir_imagen_desde_archivo(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos de Imagen", "*.png *.jpg *.jpeg"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            try:
                self.image_np = iio.imread(file_path)
                if self.image_np.ndim == 2:
                    self.image_np = np.stack([self.image_np] * 3, axis=-1)
                elif self.image_np.shape[2] == 4:
                    self.image_np = self.image_np[:, :, :3]
                self.original_image_np = self.image_np.copy()
                self.a_value = 1.0
                self.b_value = 1.0
                self.a_scale.set(1.0)
                self.b_scale.set(1.0)
                self._update_adjusted(None)
                self._update_image_display()
            except Exception as e:
                messagebox.showerror("Error al cargar imagen", f"No se pudo cargar la imagen: {e}")

    def guardar_imagen_a_archivo(self):
        if self.adjusted_vis is None:
            messagebox.showwarning("Advertencia", "No hay ninguna imagen ajustada para guardar.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPG", "*.jpg"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            try:
                iio.imwrite(file_path, self.adjusted_vis)
            except Exception as e:
                messagebox.showerror("Error al guardar imagen", f"No se pudo guardar la imagen: {e}")

    def _update_adjusted(self, value):
        self.a_value = float(self.a_scale.get())
        self.b_value = float(self.b_scale.get())
        self.a_var.set(f"{self.a_value:.2f}")
        self.b_var.set(f"{self.b_value:.2f}")
        if self.original_image_np is not None:
            try:
                estrategia = AjusteYIQ(a=self.a_value, b=self.b_value,
                                       rgb_to_yiq=self.rgb_to_yiq,
                                       yiq_to_rgb=self.yiq_to_rgb)
                self.procesador.set_estrategia(estrategia)
                self.adjusted_vis = self.procesador.procesar(self.original_image_np)
                self.image_np = self.adjusted_vis.copy()
                self._update_image_display()
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error al aplicar el ajuste YIQ: {e}")

    def _update_a_from_entry(self, event):
        try:
            new_a = float(self.a_var.get())
            if 0.1 <= new_a <= 2.0:
                self.a_value = new_a
                self.a_scale.set(new_a)
                self._update_adjusted(None)
            else:
                self.a_var.set(f"{self.a_value:.2f}")
                messagebox.showwarning("Advertencia", "El valor de 'a' debe estar entre 0.1 y 2.0.")
        except ValueError:
            self.a_var.set(f"{self.a_value:.2f}")
            messagebox.showerror("Error de Entrada", "Por favor, ingrese un número válido para 'a'.")

    def _update_b_from_entry(self, event):
        try:
            new_b = float(self.b_var.get())
            if 0.1 <= new_b <= 2.0:
                self.b_value = new_b
                self.b_scale.set(new_b)
                self._update_adjusted(None)
            else:
                self.b_var.set(f"{self.b_value:.2f}")
                messagebox.showwarning("Advertencia", "El valor de 'b' debe estar entre 0.1 y 2.0.")
        except ValueError:
            self.b_var.set(f"{self.b_value:.2f}")
            messagebox.showerror("Error de Entrada", "Por favor, ingrese un número válido para 'b'.")

    def mostrar_histograma(self):
        if self.adjusted_vis is None:
            messagebox.showwarning("Advertencia", "Cargue una imagen primero para mostrar el histograma.")
            return
        try:
            import matplotlib.pyplot as plt
            hist_window = tk.Toplevel(self.root)
            hist_window.title("Histograma de la Imagen Ajustada")
            hist_window.geometry("800x600")

            fig_hist = Figure(figsize=(7, 5), dpi=100)
            ax_hist = fig_hist.add_subplot(111)

            colors = ('b', 'g', 'r')
            for i, col in enumerate(colors):
                if i < self.adjusted_vis.shape[2]:
                    ax_hist.hist(self.adjusted_vis[:, :, i].ravel(), bins=256, range=(0, 256),
                                 color=col, alpha=0.7, label=f'Canal {["Azul", "Verde", "Rojo"][i]}')
            ax_hist.set_title('Histograma de Canales de Color (RGB) - Imagen Ajustada')
            ax_hist.set_xlabel('Intensidad de Píxel')
            ax_hist.set_ylabel('Frecuencia')
            ax_hist.legend()

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
        estrategia = RestaurarOriginal(self.original_image_np)
        self.procesador.set_estrategia(estrategia)
        self.adjusted_vis = self.procesador.procesar(self.original_image_np)
        self.image_np = self.adjusted_vis.copy()
        self.a_value = 1.0
        self.b_value = 1.0
        self.a_scale.set(1.0)
        self.b_scale.set(1.0)
        self._update_image_display()


# =======================
# Main
# =======================
if __name__ == "__main__":
    try:
        import ttkbootstrap as ttkb
        root = ttkb.Window(themename="superhero")
    except ImportError:
        print("ttkbootstrap no encontrado. Usando Tkinter estándar.")
        root = tk.Tk()

    app = ImageProcessorApp(root)
    root.mainloop()
