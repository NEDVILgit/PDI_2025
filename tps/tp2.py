import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import imageio.v3 as iio
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import sys
import os

# --- MODIFICACIÓN CLAVE: Añadir la raíz del proyecto al path ---
# Esto permite que el script encuentre 'my_functions.py' al ejecutarse de forma independiente.
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.append(project_root)
    import my_functions as mf
except ImportError:
    messagebox.showerror("Error", "No se pudo importar 'my_functions.py'. Asegúrate de que el archivo existe en la raíz del proyecto.")
    sys.exit(1)

# --- Importación de estilos visuales ---
try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
except ImportError:
    ttkb = None # Flag para saber si ttkbootstrap está disponible
    # Constantes fallback si no se encuentra ttkbootstrap
    PRIMARY, INFO, SUCCESS, DANGER = "primary", "info", "success", "danger"


class TP2Frame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.imageA_raw = None # Almacenará la imagen original (uint8)
        self.imageB_raw = None # Almacenará la imagen original (uint8)
        self.resultado = None  # Almacenará la imagen final para mostrar (uint8)
        
        self._create_widgets()
        self._setup_matplotlib_canvases()
        self._update_image_display()

    def _create_widgets(self):
        # Configuración de estilo
        style = ttk.Style()
        style.configure('TButton', font=('Segoe UI', 12, 'bold'), padding=10)

        # Frame para los controles
        workflow_frame = ttk.LabelFrame(self, text="Operaciones", padding=10)
        workflow_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Botones de Carga de Imágenes
        ttk.Button(workflow_frame, text="🖼️ Cargar Imagen A", command=lambda: self.cargar_imagen("A"), bootstyle=PRIMARY).pack(fill="x", pady=2)
        ttk.Button(workflow_frame, text="🖼️ Cargar Imagen B", command=lambda: self.cargar_imagen("B"), bootstyle=INFO).pack(fill="x", pady=2)
        ttk.Separator(workflow_frame, orient="horizontal").pack(fill="x", pady=10)

        # Combobox para seleccionar la operación
        ttk.Label(workflow_frame, text="Seleccione operación:", font=("Segoe UI", 12)).pack(pady=(10, 5))
        self.combo_op = ttk.Combobox(
            workflow_frame,
            values=[
                "Suma RGB (Clampeada)", "Suma RGB (Promediada)",
                "Resta RGB (Clampeada)", "Resta RGB (Promediada)",
                "Suma YIQ (Clampeada)", "Suma YIQ (Promediada)",
                "Resta YIQ (Clampeada)", "Resta YIQ (Promediada)",
                "Producto", "Cociente", "Resta Absoluta",
                "If-Darker", "If-Lighter",
            ],
            font=("Segoe UI", 12),
            state="readonly" # Evita que el usuario escriba texto
        )
        self.combo_op.pack(fill="x", pady=5)
        self.combo_op.current(0)

        # Botón para aplicar la operación
        ttk.Button(workflow_frame, text="▶️ Aplicar", command=self.aplicar_operacion, bootstyle=SUCCESS).pack(fill="x", pady=10)
        ttk.Separator(workflow_frame, orient="horizontal").pack(fill="x", pady=10)
        
        # Botón de salida
        ttk.Button(workflow_frame, text="❌ Salir", command=self.quit, bootstyle=DANGER).pack(fill="x", pady=5)

    def _setup_matplotlib_canvases(self):
        # Frame contenedor para los 3 visores de imágenes
        self.images_frame = ttk.Frame(self)
        self.images_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Visor para Imagen A
        imga_panel = ttk.LabelFrame(self.images_frame, text="Imagen A", padding=5)
        imga_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.fig_A = Figure(figsize=(3.5, 3.5), dpi=100)
        self.ax_A = self.fig_A.add_subplot(111)
        self.canvas_A = FigureCanvasTkAgg(self.fig_A, master=imga_panel)
        self.canvas_A.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.toolbar_imga = NavigationToolbar2Tk(self.canvas_A, imga_panel)

        # Visor para Imagen B
        imgb_panel = ttk.LabelFrame(self.images_frame, text="Imagen B", padding=5)
        imgb_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.fig_B = Figure(figsize=(3.5, 3.5), dpi=100)
        self.ax_B = self.fig_B.add_subplot(111)
        self.canvas_B = FigureCanvasTkAgg(self.fig_B, master=imgb_panel)
        self.canvas_B.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.toolbar_imgb = NavigationToolbar2Tk(self.canvas_B, imgb_panel)

        # Visor para el Resultado
        imgres_panel = ttk.LabelFrame(self.images_frame, text="Imagen Resultado", padding=5)
        imgres_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.fig_res = Figure(figsize=(3.5, 3.5), dpi=100)
        self.ax_res = self.fig_res.add_subplot(111)
        self.canvas_res = FigureCanvasTkAgg(self.fig_res, master=imgres_panel)
        self.canvas_res.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.toolbar_imgres = NavigationToolbar2Tk(self.canvas_res, imgres_panel)

    def _update_image_display(self):
        # Función para dibujar una imagen en un eje de Matplotlib
        def draw_image(ax, canvas, image, title):
            ax.clear()
            if image is not None:
                ax.imshow(image)
                ax.set_title(title)
            else:
                ax.text(0.5, 0.5, f"No hay imagen\n{title}", ha="center", va="center")
            ax.axis("off")
            canvas.draw_idle()

        draw_image(self.ax_A, self.canvas_A, self.imageA_raw, "Imagen A")
        draw_image(self.ax_B, self.canvas_B, self.imageB_raw, "Imagen B")
        draw_image(self.ax_res, self.canvas_res, self.resultado, "Resultado")

    def cargar_imagen(self, cual):
        file_path = filedialog.askopenfilename(
            title=f"Seleccionar Imagen {cual}",
            filetypes=[("Archivos de Imagen", "*.png *.jpg *.jpeg *.bmp"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return
        try:
            img = iio.imread(file_path)
            # Asegurarse de que la imagen sea RGB (eliminar canal alfa si existe)
            if img.ndim == 3 and img.shape[2] == 4:
                img = img[:, :, :3]
            
            if cual == "A":
                self.imageA_raw = img
            else:
                self.imageB_raw = img
            self._update_image_display()
        except Exception as e:
            messagebox.showerror("Error al cargar imagen", str(e))

    def _prepare_images(self):
        """
        Verifica, recorta al tamaño común más pequeño y convierte las imágenes
        a formato de punto flotante en el rango [0, 1].
        """
        if self.imageA_raw is None or self.imageB_raw is None:
            messagebox.showwarning("Imágenes Faltantes", "Debe cargar ambas imágenes (A y B) para continuar.")
            return None, None
        
        # Recortar a las dimensiones mínimas comunes
        min_h = min(self.imageA_raw.shape[0], self.imageB_raw.shape[0])
        min_w = min(self.imageA_raw.shape[1], self.imageB_raw.shape[1])
        
        imgA_cut = self.imageA_raw[:min_h, :min_w]
        imgB_cut = self.imageB_raw[:min_h, :min_w]
        
        # Convertir a flotante en rango [0, 1]
        imgA_float = imgA_cut.astype(np.float32) / 255.0
        imgB_float = imgB_cut.astype(np.float32) / 255.0
        
        return imgA_float, imgB_float

    def aplicar_operacion(self):
        """
        Orquesta la aplicación de la operación: prepara las imágenes,
        llama a la función correspondiente de my_functions y muestra el resultado.
        """
        imgA, imgB = self._prepare_images()
        if imgA is None:
            return

        operaciones = {
            "Suma RGB (Clampeada)": mf.suma_rgb_clampeada,
            "Suma RGB (Promediada)": mf.suma_rgb_promediada,
            "Resta RGB (Clampeada)": mf.resta_rgb_clampeada,
            "Resta RGB (Promediada)": mf.resta_rgb_promediada,
            "Suma YIQ (Clampeada)": mf.suma_yiq_clampeada,
            "Suma YIQ (Promediada)": mf.suma_yiq_promediada,
            "Resta YIQ (Clampeada)": mf.resta_yiq_clampeada,
            "Resta YIQ (Promediada)": mf.resta_yiq_promediada,
            "Producto": mf.producto,
            "Cociente": mf.cociente,
            "Resta Absoluta": mf.resta_absoluta,
            "If-Darker": mf.if_darker,
            "If-Lighter": mf.if_lighter,
        }
        
        op_seleccionada = self.combo_op.get()
        funcion_a_llamar = operaciones.get(op_seleccionada)
        
        if funcion_a_llamar:
            # 1. Llamar a la función de my_functions (trabaja con flotantes)
            resultado_float = funcion_a_llamar(imgA, imgB)
            
            # 2. Convertir el resultado de vuelta a uint8 para poder mostrarlo
            self.resultado = (np.clip(resultado_float, 0, 1) * 255).astype(np.uint8)
            
            # 3. Actualizar la GUI
            self._update_image_display()
        else:
            messagebox.showerror("Error", f"La operación '{op_seleccionada}' no está implementada.")


def main():
    """Función principal para lanzar la aplicación del TP2."""
    if ttkb:
        # Usar ttkbootstrap si está disponible
        root = ttkb.Window(themename="superhero")
    else:
        # Usar tkinter estándar como fallback
        root = tk.Tk()
        # Se podrían agregar configuraciones de estilo para tkinter aquí
        
    root.title("Trabajo Práctico 2 - Operaciones entre Imágenes")
    root.geometry("1400x650")
    
    app_frame = TP2Frame(root)
    app_frame.pack(fill="both", expand=True)
    
    root.mainloop()

# --- Bloque de ejecución ---
# Esto permite que el script se ejecute directamente con 'python tps/tp2.py'
if __name__ == "__main__":
    main()
