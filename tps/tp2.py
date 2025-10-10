import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import imageio.v3 as iio
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
except ImportError:
    ttkb = None
    PRIMARY, INFO, SUCCESS, DANGER = "", "", "", ""  # Fallback for bootstyle constants

class TP2Frame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.imageA = None
        self.imageB = None
        self.resultado = None
        self._create_widgets()
        self._setup_matplotlib_canvases()
        self._update_image_display()

    def _create_widgets(self):
        # Configure button style
        style = ttk.Style()
        style.configure('TButton', font=('Segoe UI', 12, 'bold'), padding=10)

        workflow_frame = ttk.LabelFrame(self, text="Operaciones", padding=10)
        workflow_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        ttk.Button(
            workflow_frame,
            text="🖼️ Cargar Imagen A",
            bootstyle=PRIMARY,
            width=20,
            command=lambda: self.cargar_imagen("A")
        ).pack(fill="x", pady=2)
        ttk.Button(
            workflow_frame,
            text="🖼️ Cargar Imagen B",
            bootstyle=INFO,
            width=20,
            command=lambda: self.cargar_imagen("B")
        ).pack(fill="x", pady=2)
        ttk.Separator(workflow_frame, orient="horizontal").pack(fill="x", pady=5)

        ttk.Label(workflow_frame, text="Seleccione operación:", font=("Segoe UI", 12)).pack(pady=5)
        self.combo_op = ttk.Combobox(
            workflow_frame,
            values=[
                "Suma RGB (Clampeada)",
                "Suma RGB (Promediada)",
                "Resta RGB (Clampeada)",
                "Resta RGB (Promediada)",
                "Suma YIQ (Clampeada)",
                "Suma YIQ (Promediada)",
                "Resta YIQ (Clampeada)",
                "Resta YIQ (Promediada)",
                "Producto",
                "Cociente",
                "Resta Absoluta",
                "If-Darker",
                "If-Lighter",
            ],
            font=("Segoe UI", 12)
        )
        self.combo_op.pack(fill="x", pady=5)
        self.combo_op.current(0)

        ttk.Button(
            workflow_frame,
            text="▶️ Aplicar",
            bootstyle=SUCCESS,
            width=20,
            command=self.aplicar_operacion
        ).pack(fill="x", pady=10)
        ttk.Separator(workflow_frame, orient="horizontal").pack(fill="x", pady=5)
        ttk.Button(
            workflow_frame,
            text="❌ Salir",
            bootstyle=DANGER,
            width=20,
            command=self.quit
        ).pack(fill="x", pady=5)

    def _setup_matplotlib_canvases(self):
        self.images_frame = ttk.Frame(self)
        self.images_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        imga_panel = ttk.LabelFrame(self.images_frame, text="Imagen A", padding=5)
        imga_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.fig_A = Figure(figsize=(3.5, 3.5), dpi=100)
        self.ax_A = self.fig_A.add_subplot(111)
        self.canvas_A = FigureCanvasTkAgg(self.fig_A, master=imga_panel)
        self.canvas_A.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.toolbar_imga = NavigationToolbar2Tk(self.canvas_A, imga_panel)
        self.toolbar_imga.update()
        self.label_imga_info = ttk.Label(imga_panel, text="Dimensiones: N/A\nTipo de Dato: N/A", font=("Segoe UI", 10))
        self.label_imga_info.pack(pady=5)

        imgb_panel = ttk.LabelFrame(self.images_frame, text="Imagen B", padding=5)
        imgb_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.fig_B = Figure(figsize=(3.5, 3.5), dpi=100)
        self.ax_B = self.fig_B.add_subplot(111)
        self.canvas_B = FigureCanvasTkAgg(self.fig_B, master=imgb_panel)
        self.canvas_B.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.toolbar_imgb = NavigationToolbar2Tk(self.canvas_B, imgb_panel)
        self.toolbar_imgb.update()
        self.label_imgb_info = ttk.Label(imgb_panel, text="Dimensiones: N/A\nTipo de Dato: N/A", font=("Segoe UI", 10))
        self.label_imgb_info.pack(pady=5)

        imgres_panel = ttk.LabelFrame(self.images_frame, text="Imagen Resultado", padding=5)
        imgres_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.fig_res = Figure(figsize=(3.5, 3.5), dpi=100)
        self.ax_res = self.fig_res.add_subplot(111)
        self.canvas_res = FigureCanvasTkAgg(self.fig_res, master=imgres_panel)
        self.canvas_res.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.toolbar_imgres = NavigationToolbar2Tk(self.canvas_res, imgres_panel)
        self.toolbar_imgres.update()
        self.label_imgres_info = ttk.Label(imgres_panel, text="Dimensiones: N/A\nTipo de Dato: N/A", font=("Segoe UI", 10))
        self.label_imgres_info.pack(pady=5)

    def _update_image_display(self):
        self.ax_A.clear()
        if self.imageA is not None:
            self.ax_A.imshow(self.imageA)
            self.ax_A.set_title("Imagen A")
            self.label_imga_info.config(
                text=f"Dimensiones: {self.imageA.shape}\nTipo de Dato: {self.imageA.dtype}"
            )
        else:
            self.ax_A.text(0.5, 0.5, "No hay A", ha="center", va="center")
            self.label_imga_info.config(text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.ax_A.axis("off")
        self.canvas_A.draw_idle()

        self.ax_B.clear()
        if self.imageB is not None:
            self.ax_B.imshow(self.imageB)
            self.ax_B.set_title("Imagen B")
            self.label_imgb_info.config(
                text=f"Dimensiones: {self.imageB.shape}\nTipo de Dato: {self.imageB.dtype}"
            )
        else:
            self.ax_B.text(0.5, 0.5, "No hay B", ha="center", va="center")
            self.label_imgb_info.config(text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.ax_B.axis("off")
        self.canvas_B.draw_idle()

        self.ax_res.clear()
        if self.resultado is not None:
            self.ax_res.imshow(self.resultado)
            self.ax_res.set_title("Resultado")
            self.label_imgres_info.config(
                text=f"Dimensiones: {self.resultado.shape}\nTipo de Dato: {self.resultado.dtype}"
            )
        else:
            self.ax_res.text(0.5, 0.5, "Sin resultado", ha="center", va="center")
            self.label_imgres_info.config(text="Dimensiones: N/A\nTipo de Dato: N/A")
        self.ax_res.axis("off")
        self.canvas_res.draw_idle()

    def cargar_imagen(self, cual):
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos de Imagen", "*.png *.jpg *.jpeg"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            try:
                img = iio.imread(file_path)
                if cual == "A":
                    self.imageA = img
                else:
                    self.imageB = img
                self._update_image_display()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def ajustar_tamanios(self):
        if self.imageA is None or self.imageB is None:
            messagebox.showwarning("Advertencia", "Debe cargar ambas imágenes.")
            return None, None
        min_h = min(self.imageA.shape[0], self.imageB.shape[0])
        min_w = min(self.imageA.shape[1], self.imageB.shape[1])
        return self.imageA[:min_h, :min_w], self.imageB[:min_h, :min_w]

    def rgb_to_yiq(self, img):
        img_norm = img / 255.0
        T = np.array([[0.299, 0.587, 0.114],
                      [0.596, -0.274, -0.322],
                      [0.211, -0.523, 0.312]])
        return img_norm @ T.T

    def yiq_to_rgb(self, yiq):
        T_inv = np.array([[1, 0.956, 0.621],
                          [1, -0.272, -0.647],
                          [1, -1.106, 1.703]])
        rgb = yiq @ T_inv.T
        rgb = np.clip(rgb, 0, 1) * 255
        return rgb.astype(np.uint8)

    def aplicar_operacion(self):
        operaciones = {
            "Suma RGB (Clampeada)": self.suma_rgb_clampeada,
            "Suma RGB (Promediada)": self.suma_rgb_promediada,
            "Resta RGB (Clampeada)": self.resta_rgb_clampeada,
            "Resta RGB (Promediada)": self.resta_rgb_promediada,
            "Suma YIQ (Clampeada)": self.suma_yiq_clampeada,
            "Suma YIQ (Promediada)": self.suma_yiq_promediada,
            "Resta YIQ (Clampeada)": self.resta_yiq_clampeada,
            "Resta YIQ (Promediada)": self.resta_yiq_promediada,
            "Producto": self.producto,
            "Cociente": self.cociente,
            "Resta Absoluta": self.resta_abs,
            "If-Darker": self.if_darker,
            "If-Lighter": self.if_lighter,
        }
        op = self.combo_op.get()
        if op in operaciones:
            operaciones[op]()

    def suma_rgb_clampeada(self):
        imgA, imgB = self.ajustar_tamanios()
        if imgA is None: return
        self.resultado = np.clip(imgA.astype(np.int32) + imgB.astype(np.int32), 0, 255).astype(np.uint8)
        self._update_image_display()

    def suma_rgb_promediada(self):
        imgA, imgB = self.ajustar_tamanios()
        if imgA is None: return
        self.resultado = ((imgA.astype(np.float32) + imgB.astype(np.float32)) / 2).astype(np.uint8)
        self._update_image_display()

    def resta_rgb_clampeada(self):
        imgA, imgB = self.ajustar_tamanios()
        if imgA is None: return
        self.resultado = np.clip(imgA.astype(np.int32) - imgB.astype(np.int32), 0, 255).astype(np.uint8)
        self._update_image_display()

    def resta_rgb_promediada(self):
        imgA, imgB = self.ajustar_tamanios()
        if imgA is None: return
        self.resultado = ((imgA.astype(np.float32) - imgB.astype(np.float32)) / 2 + 127).clip(0, 255).astype(np.uint8)
        self._update_image_display()

    def suma_yiq_clampeada(self):
        imgA, imgB = self.ajustar_tamanios()
        if imgA is None: return
        yiqA, yiqB = self.rgb_to_yiq(imgA), self.rgb_to_yiq(imgB)
        yiq_res = np.clip(yiqA + yiqB, 0, 1)
        self.resultado = self.yiq_to_rgb(yiq_res)
        self._update_image_display()

    def suma_yiq_promediada(self):
        imgA, imgB = self.ajustar_tamanios()
        if imgA is None: return
        yiqA, yiqB = self.rgb_to_yiq(imgA), self.rgb_to_yiq(imgB)
        yiq_res = (yiqA + yiqB) / 2
        yiq_res[..., 0] = np.clip(yiq_res[..., 0], 0, 1)
        yiq_res[..., 1] = np.clip(yiq_res[..., 1], -0.5957, 0.5957)
        yiq_res[..., 2] = np.clip(yiq_res[..., 2], -0.5226, 0.5226)
        self.resultado = self.yiq_to_rgb(yiq_res)
        self._update_image_display()

    def resta_yiq_clampeada(self):
        imgA, imgB = self.ajustar_tamanios()
        if imgA is None: return
        yiqA, yiqB = self.rgb_to_yiq(imgA), self.rgb_to_yiq(imgB)
        yiq_res = np.clip(yiqA - yiqB, 0, 1)
        self.resultado = self.yiq_to_rgb(yiq_res)
        self._update_image_display()

    def resta_yiq_promediada(self):
        imgA, imgB = self.ajustar_tamanios()
        if imgA is None: return
        yiqA, yiqB = self.rgb_to_yiq(imgA), self.rgb_to_yiq(imgB)
        yiq_res = (yiqA - yiqB) / 2
        yiq_res[..., 0] = np.clip(yiq_res[..., 0], 0, 1)
        yiq_res[..., 1] = np.clip(yiq_res[..., 1], -0.5957, 0.5957)
        yiq_res[..., 2] = np.clip(yiq_res[..., 2], -0.5226, 0.5226)
        self.resultado = self.yiq_to_rgb(yiq_res)
        self._update_image_display()

    def producto(self):
        imgA, imgB = self.ajustar_tamanios()
        if imgA is None: return
        self.resultado = np.clip((imgA.astype(np.float32) * imgB.astype(np.float32)) / 255.0, 0, 255).astype(np.uint8)
        self._update_image_display()

    def cociente(self):
        imgA, imgB = self.ajustar_tamanios()
        if imgA is None: return
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.true_divide(imgA.astype(np.float32), imgB.astype(np.float32) + 1e-8)
            ratio = np.clip(ratio * 128, 0, 255)
        self.resultado = ratio.astype(np.uint8)
        self._update_image_display()

    def resta_abs(self):
        imgA, imgB = self.ajustar_tamanios()
        if imgA is None: return
        self.resultado = np.abs(imgA.astype(np.int32) - imgB.astype(np.int32)).astype(np.uint8)
        self._update_image_display()

    def if_darker(self):
        imgA, imgB = self.ajustar_tamanios()
        if imgA is None: return
        self.resultado = np.minimum(imgA, imgB).astype(np.uint8)
        self._update_image_display()

    def if_lighter(self):
        imgA, imgB = self.ajustar_tamanios()
        if imgA is None: return
        self.resultado = np.maximum(imgA, imgB).astype(np.uint8)
        self._update_image_display()

def main():
    if ttkb:
        root = ttkb.Window(themename="superhero")
    else:
        root = tk.Tk()
    root.title("Procesamiento de Imágenes - TP2")
    root.geometry("1400x600")
    app = TP2Frame(root)
    app.pack(fill="both", expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()