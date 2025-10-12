import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from scipy.special import erfinv, erf  # Agregado erf para gráfico

class FilterWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Filtro Pasabanda")
        self.geometry("600x800")
        self.resizable(True, True)
        self.parent = parent

        # Style configuration
        style = ttk.Style()
        style.configure('TButton', font=('Segoe UI', 12, 'bold'), padding=10)
        style.configure('TRadiobutton', font=('Segoe UI', 10))
        style.configure('TLabel', font=('Segoe UI', 10))

        # Title
        title_label = ttk.Label(
            self,
            text="Seleccione un Filtro",
            font=("Segoe UI", 16, "bold"),
            anchor="center"
        )
        title_label.pack(pady=20)

        # Filter selection
        filter_frame = ttk.Frame(self)
        filter_frame.pack(pady=10, padx=20, fill="x")

        ttk.Radiobutton(filter_frame, text="Raiz Cuadrada", variable=parent.filter_var, value="Raiz Cuadrada").pack(anchor="w", pady=5)
        ttk.Radiobutton(filter_frame, text="Filtro Cuadratico", variable=parent.filter_var, value="Filtro Cuadratico").pack(anchor="w", pady=5)
        ttk.Radiobutton(filter_frame, text="Filtro Lineal", variable=parent.filter_var, value="Filtro Lineal").pack(anchor="w", pady=5)
        ttk.Radiobutton(filter_frame, text="Normalizacion", variable=parent.filter_var, value="Normalizacion").pack(anchor="w", pady=5)
        ttk.Radiobutton(filter_frame, text="Ecualizacion", variable=parent.filter_var, value="Ecualizacion").pack(anchor="w", pady=5)

        # Sliders frame (inicialmente no empaquetado)
        self.slider_frame = ttk.Frame(self)
        self.slider_frame._packed = False  # Flag para controlar visibilidad

        ttk.Label(self.slider_frame, text="Luminancia de corte inferior").pack()
        self.lower_scale = ttk.Scale(self.slider_frame, from_=0.0, to=1.0, orient="horizontal", variable=parent.lower_cutoff)
        self.lower_scale.pack(fill="x", pady=5)

        ttk.Label(self.slider_frame, text="Luminancia de corte superior").pack()
        self.upper_scale = ttk.Scale(self.slider_frame, from_=0.0, to=1.0, orient="horizontal", variable=parent.upper_cutoff)
        self.upper_scale.pack(fill="x", pady=5)

        # Graph
        self.fig = plt.Figure(figsize=(4, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(pady=10, padx=20, fill="both", expand=True)

        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=20, padx=20)

        ttk.Button(
            button_frame,
            text="Aplicar Filtro",
            bootstyle=PRIMARY,
            width=15,
            command=self.apply_filter
        ).pack(side="left", padx=10)

        ttk.Button(
            button_frame,
            text="Cerrar",
            bootstyle=DANGER,
            width=15,
            command=self.destroy
        ).pack(side="right", padx=10)

        # Footer
        footer = ttk.Label(
            self,
            text="Desarrollado por [Tu Nombre]",
            font=("Segoe UI", 9),
            anchor="center",
            foreground="#AAAAAA"
        )
        footer.pack(side="bottom", pady=10)

        # Traces
        parent.filter_var.trace("w", self.update_graph)
        parent.lower_cutoff.trace("w", self.update_graph)
        parent.upper_cutoff.trace("w", self.update_graph)

        self.update_graph()

    def update_graph(self, *args):
        self.ax.clear()
        x = np.linspace(0, 1, 100)
        filter_type = self.parent.filter_var.get()
        
        # Manejo de sliders: mostrar solo para Filtro Lineal
        if filter_type == "Filtro Lineal":
            if not self.slider_frame._packed:
                self.slider_frame.pack(pady=10, padx=20, fill="x")
                self.slider_frame._packed = True
        else:
            if self.slider_frame._packed:
                self.slider_frame.pack_forget()
                self.slider_frame._packed = False

        if filter_type == "Raiz Cuadrada":
            y = np.sqrt(x)
        elif filter_type == "Filtro Cuadratico":
            y = x ** 2
        elif filter_type == "Filtro Lineal":
            ymin = self.parent.lower_cutoff.get()
            ymax = self.parent.upper_cutoff.get()
            y = np.piecewise(x, [x < ymin, (x >= ymin) & (x <= ymax), x > ymax],
                             [0, lambda xi: (xi - ymin) / (ymax - ymin) if ymax > ymin else 0.5, 1])
        elif filter_type == "Normalizacion":
            # Aproximación de la curva erf (media 0.5, std 0.1)
            target_mean = 0.5
            target_std = 0.1
            u = x  # Placeholder para ecualización
            z = erfinv(2 * u - 1)
            y = target_mean + target_std * np.sqrt(2) * z
            y = np.clip(y, 0, 1)
            self.ax.text(0.5, 0.5, "Erf-based (data-dependent)", ha="center", va="center", transform=self.ax.transAxes, fontsize=10)
        elif filter_type == "Ecualizacion":
            y = x  # Placeholder
            self.ax.text(0.5, 0.5, "Data-dependent (CDF)", ha="center", va="center", transform=self.ax.transAxes, fontsize=10)
        
        self.ax.plot(x, y, color='black', linewidth=2)
        self.ax.set_xlabel("Luminancia de Entrada")
        self.ax.set_ylabel("Luminancia de Salida")
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.grid(True)
        self.canvas.draw()

    def apply_filter(self):
        self.parent.apply_filter()
        self.destroy()

class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        self.title("Histogramas - PDI UNS 2007")
        self.geometry("900x700")
        self.resizable(False, False)

        # Style configuration
        style = ttk.Style()
        style.configure('TButton', font=('Segoe UI', 12, 'bold'), padding=10)
        style.configure('TLabel', font=('Segoe UI', 10))

        # Variables
        self.filter_var = tk.StringVar(value="Raiz Cuadrada")
        self.lower_cutoff = tk.DoubleVar(value=0.2)
        self.upper_cutoff = tk.DoubleVar(value=0.8)
        self.image = None
        self.processed = None

        # Title
        title_label = ttk.Label(
            self,
            text="Procesamiento Digital de Imágenes",
            font=("Segoe UI", 18, "bold"),
            anchor="center"
        )
        title_label.pack(pady=20)

        # Images frame
        images_frame = ttk.Frame(self)
        images_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.original_label = ttk.Label(images_frame, text="Imagen Original")
        self.original_label.pack(side="left", padx=20, pady=10, expand=True)

        self.processed_label = ttk.Label(images_frame, text="Imagen Procesada")
        self.processed_label.pack(side="right", padx=20, pady=10, expand=True)

        # Bottom buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=20, padx=20, fill="x")

        ttk.Button(
            button_frame,
            text="Cargar",
            bootstyle=PRIMARY,
            width=15,
            command=self.load_image
        ).pack(side="left", padx=10)

        ttk.Button(
            button_frame,
            text="Histograma",
            bootstyle=INFO,
            width=15,
            command=self.show_histogram
        ).pack(side="left", padx=10)

        ttk.Button(
            button_frame,
            text="Elegir Filtro",
            bootstyle=SUCCESS,
            width=15,
            command=self.open_filter_window
        ).pack(side="left", padx=10)

        ttk.Button(
            button_frame,
            text="Salir",
            bootstyle=DANGER,
            width=15,
            command=self.quit
        ).pack(side="right", padx=10)

        # Footer
        footer = ttk.Label(
            self,
            text="Desarrollado por [Tu Nombre]",
            font=("Segoe UI", 9),
            anchor="center",
            foreground="#AAAAAA"
        )
        footer.pack(side="bottom", pady=10)

    def open_filter_window(self):
        FilterWindow(self)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.bmp *.jpeg *.tiff")])
        if path and path != "":
            self.image = cv2.imread(path)
            if self.image is not None:  # Validación básica
                self.show_image(self.image, self.original_label)
                self.processed = None
                self.show_image(self.processed, self.processed_label)
            else:
                tk.messagebox.showerror("Error", "No se pudo cargar la imagen. Verifica el archivo.")

    def show_image(self, img, label):
        label.config(text="")  # Ocultar texto cuando hay imagen
        if img is None:
            label.config(text="Sin imagen")  # Texto por defecto
            label.config(image="")
            return
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        pil_img = pil_img.resize((300, 300), Image.LANCZOS)
        photo = ImageTk.PhotoImage(pil_img)
        label.config(image=photo)
        label.image = photo  # Mantener referencia

    def apply_filter(self):
        if self.image is None:
            tk.messagebox.showwarning("Advertencia", "Carga una imagen primero.")
            return
        img_norm = self.image.astype(np.float32) / 255.0
        yiq = self.rgb_to_yiq(img_norm)
        y = yiq[..., 0]
        filter_type = self.filter_var.get()
        if filter_type == "Raiz Cuadrada":
            y_new = np.sqrt(y)
        elif filter_type == "Filtro Cuadratico":
            y_new = y ** 2
        elif filter_type == "Filtro Lineal":
            ymin = self.lower_cutoff.get()
            ymax = self.upper_cutoff.get()
            y_new = np.zeros_like(y)
            mask_low = y < ymin
            mask_high = y > ymax
            mask_mid = ~(mask_low | mask_high)
            y_new[mask_low] = 0
            y_new[mask_high] = 1
            if ymax > ymin:
                y_new[mask_mid] = (y[mask_mid] - ymin) / (ymax - ymin)
            else:
                y_new[mask_mid] = 0.5  # Evitar div/0
        elif filter_type == "Ecualizacion":
            y_new = self.histogram_equalization(y)
        elif filter_type == "Normalizacion":
            y_new = self.histogram_normalization(y)
        yiq[..., 0] = y_new
        rgb_new = self.yiq_to_rgb(yiq)
        rgb_new = np.clip(rgb_new, 0, 1) * 255
        self.processed = rgb_new.astype(np.uint8)
        self.show_image(self.processed, self.processed_label)

    def rgb_to_yiq(self, rgb):
        r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        y = 0.299 * r + 0.587 * g + 0.114 * b
        i = 0.596 * r - 0.275 * g - 0.321 * b
        q = 0.212 * r - 0.523 * g + 0.311 * b
        return np.stack([y, i, q], axis=-1)

    def yiq_to_rgb(self, yiq):
        y, i, q = yiq[..., 0], yiq[..., 1], yiq[..., 2]
        r = y + 0.956 * i + 0.621 * q
        g = y - 0.272 * i - 0.647 * q
        b = y - 1.107 * i + 1.704 * q
        return np.stack([r, g, b], axis=-1)

    def histogram_equalization(self, y):
        y_flat = y.flatten()
        hist, bins = np.histogram(y_flat, bins=256, range=(0, 1))
        cdf = hist.cumsum()
        cdf_normalized = cdf * 255 / cdf[-1]  # Escalar a 0-255, pero como y es [0,1], ajustamos
        y_new = np.interp(y_flat, bins[:-1], cdf_normalized / 255.0)
        return y_new.reshape(y.shape)

    def histogram_normalization(self, y):
        target_mean = 0.5
        target_std = 0.1
        u = self.histogram_equalization(y)
        z = erfinv(2 * u - 1)
        y_new = target_mean + target_std * np.sqrt(2) * z
        y_new = np.clip(y_new, 0, 1)
        return y_new

    def show_histogram(self):
        if self.image is None:
            tk.messagebox.showwarning("Advertencia", "Carga una imagen primero.")
            return
        img_norm = self.image.astype(np.float32) / 255.0
        yiq = self.rgb_to_yiq(img_norm)
        y = yiq[..., 0]
        plt.clf()  # Limpiar figura anterior
        fig, ax = plt.subplots()
        counts, bins = np.histogram(y, bins=50, range=(0, 1))  # Más bins para detalle
        ax.bar(bins[:-1], (counts / counts.sum()) * 100, width=np.diff(bins), align='edge', color='blue', alpha=0.7)
        ax.set_xlabel("Luminancia")
        ax.set_ylabel("Frec. relativa de aparición (%)")
        ax.set_xlim(0, 1)
        ax.set_title("Histograma de Luminancia")
        plt.show()

if __name__ == "__main__":
    app = App()
    app.mainloop()
