import numpy as np
from scipy.special import erfinv # Para la normalización del histograma
from scipy.ndimage import minimum_filter, maximum_filter, median_filter

# --- CONSTANTES Y CONVERSIÓN ---

""" Matriz de conversión de RGB a YIQ """
MAT_RGB_TO_YIQ = np.array([[0.299, 0.587, 0.114],
                         [0.596, -0.274, -0.322],
                         [0.211, -0.523, 0.312]]).T

""" Matriz de conversión de YIQ a RGB """
MAT_YIQ_TO_RGB = np.linalg.inv(MAT_RGB_TO_YIQ)


def rgb2yiq(im_rgb):
    """Convierte una imagen de RGB a YIQ de forma eficiente."""
    return im_rgb @ MAT_RGB_TO_YIQ

def yiq2rgb(im_yiq):
    """Convierte una imagen de YIQ a RGB de forma eficiente."""
    im_rgb = im_yiq @ MAT_YIQ_TO_RGB
    return np.clip(im_rgb, 0, 1)

# --- OPERACIONES ARITMÉTICAS ---

# --- Sumas RGB ---
def suma_rgb_clampeada(im1, im2):
  """Suma directa y recorta el resultado si supera el rango [0, 1]."""
  return np.clip(im1 + im2, 0, 1)

def suma_rgb_promediada(im1, im2):
  """Suma las imágenes y las divide por 2 para obtener un promedio."""
  return (im1 + im2) / 2.0

# --- Restas RGB ---
def resta_rgb_clampeada(im1, im2):
  """Resta directa y recorta el resultado si es menor que 0."""
  return np.clip(im1 - im2, 0, 1)

def resta_rgb_promediada(im1, im2):
    """
    Calcula la diferencia y la normaliza. El gris (0.5) representa 'sin diferencia'.
    Mapea el rango de resultado [-1, 1] al rango visible [0, 1].
    """
    return (im1 - im2) / 2.0 + 0.5

def resta_absoluta(im1, im2):
  """Calcula la diferencia absoluta (brillo) entre dos imágenes RGB."""
  return np.abs(im1 - im2)

# --- Operaciones YIQ ---
def _operacion_yiq(im1, im2, operacion):
    """Función auxiliar para realizar operaciones en el espacio YIQ."""
    yiq1 = rgb2yiq(im1)
    yiq2 = rgb2yiq(im2)
    resultado_yiq = operacion(yiq1, yiq2)

    # Clampeo específico para los componentes Y, I, Q
    resultado_yiq[:, :, 0] = np.clip(resultado_yiq[:, :, 0], 0, 1)      # Y: [0, 1]
    resultado_yiq[:, :, 1] = np.clip(resultado_yiq[:, :, 1], -0.5957, 0.5957) # I
    resultado_yiq[:, :, 2] = np.clip(resultado_yiq[:, :, 2], -0.5226, 0.5226) # Q

    return yiq2rgb(resultado_yiq)

def suma_yiq_clampeada(im1, im2):
    return _operacion_yiq(im1, im2, lambda yiq1, yiq2: yiq1 + yiq2)

def suma_yiq_promediada(im1, im2):
    return _operacion_yiq(im1, im2, lambda yiq1, yiq2: (yiq1 + yiq2) / 2.0)

def resta_yiq_clampeada(im1, im2):
    return _operacion_yiq(im1, im2, lambda yiq1, yiq2: yiq1 - yiq2)

def resta_yiq_promediada(im1, im2):
    return _operacion_yiq(im1, im2, lambda yiq1, yiq2: (yiq1 - yiq2) / 2.0)

# --- Multiplicación y División ---
def producto(im1, im2):
    """Multiplica los valores de los píxeles. Útil para máscaras."""
    return im1 * im2

def cociente(im1, im2):
    """
    Divide los valores de los píxeles. Se añade epsilon para evitar división por cero.
    El resultado se escala para una mejor visualización.
    """
    # Se multiplica por 0.5 para que el resultado no sea excesivamente brillante
    return np.clip((im1 / (im2 + 1e-8)) * 0.5, 0, 1)

# --- FUNCIONES DE COMPOSICIÓN ---

def if_darker(im1, im2):
    """Crea una imagen nueva usando el píxel más oscuro (menor luminancia Y) de cada imagen."""
    yiq1 = rgb2yiq(im1)
    yiq2 = rgb2yiq(im2)
    # Crea una máscara booleana. True donde el píxel de im1 es más oscuro.
    mask = yiq1[:, :, 0] < yiq2[:, :, 0]
    # np.newaxis expande la máscara para que aplique a los 3 canales RGB
    return np.where(mask[..., np.newaxis], im1, im2)

def if_lighter(im1, im2):
    """Crea una imagen nueva usando el píxel más claro (mayor luminancia Y) de cada imagen."""
    yiq1 = rgb2yiq(im1)
    yiq2 = rgb2yiq(im2)
    mask = yiq1[:, :, 0] > yiq2[:, :, 0]
    return np.where(mask[..., np.newaxis], im1, im2)

# ===================================================================
# --- NUEVAS FUNCIONES PARA TP3: MANIPULACIÓN DE LUMINANCIA ---
# ===================================================================

def filtro_raiz(y_channel):
    """
    Aplica una función de raíz cuadrada a la luminancia.
    Aclara las zonas oscuras más que las claras, mejorando imágenes subexpuestas.
    Y' = sqrt(Y)
    """
    return np.sqrt(y_channel)

def filtro_cuadratico(y_channel):
    """
    Aplica una función cuadrática a la luminancia.
    Oscurece las zonas claras más que las oscuras, mejorando imágenes sobreexpuestas.
    Y' = Y^2
    """
    return y_channel ** 2

def filtro_lineal_a_trozos(y_channel, y_min, y_max):
    """
    Expande el rango dinámico de la imagen.
    Mapea el intervalo de luminancia [y_min, y_max] al rango completo [0, 1].
    """
    if y_max <= y_min:
        # Evita división por cero y devuelve una imagen de contraste medio
        return np.full_like(y_channel, 0.5)

    # Copiamos para no modificar el original
    y_new = y_channel.copy()
    
    # Zonas por debajo del mínimo se mapean a 0
    y_new[y_channel < y_min] = 0
    # Zonas por encima del máximo se mapean a 1
    y_new[y_channel > y_max] = 1
    
    # Zonas intermedias se estiran linealmente
    mask = (y_channel >= y_min) & (y_channel <= y_max)
    y_new[mask] = (y_channel[mask] - y_min) / (y_max - y_min)
    
    return y_new

def ecualizacion_histograma(y_channel):
    """
    Redistribuye las luminancias para que cada nivel tenga aproximadamente
    la misma cantidad de píxeles. Esto generalmente aumenta el contraste global.
    """
    # Se aplana el array 2D a 1D para calcular el histograma
    y_flat = y_channel.flatten()
    
    # Se calcula el histograma y la función de distribución acumulada (CDF)
    hist, bins = np.histogram(y_flat, bins=256, range=(0, 1))
    cdf = hist.cumsum()
    
    # Se normaliza la CDF para que actúe como una tabla de mapeo (LUT)
    cdf_normalized = (cdf - cdf.min()) * 255 / (cdf.max() - cdf.min())
    
    # Se mapean los valores de luminancia originales a sus nuevos valores ecualizados
    y_equalized = np.interp(y_flat, bins[:-1], cdf_normalized / 255.0)
    
    # Se devuelve el canal Y con la forma original de la imagen
    return y_equalized.reshape(y_channel.shape)

def normalizacion_histograma(y_channel, target_mean=0.5, target_std=0.15):
    """
    Ajusta la distribución de luminancia para que se asemeje a una
    distribución Gaussiana (Normal) con una media y desviación estándar dadas.
    """
    # Primero, ecualizamos para obtener una distribución uniforme, que es un
    # requisito previo para aplicar la función de error inversa (erfinv).
    u = ecualizacion_histograma(y_channel)
    
    # La función inversa de error (erfinv) transforma la distribución uniforme
    # en una distribución normal estándar (media 0, std 1).
    # Se añade un pequeño epsilon para evitar erfinv(1) o erfinv(-1) que son infinitos.
    z = erfinv(2 * np.clip(u, 1e-6, 1 - 1e-6) - 1) * np.sqrt(2)
    
    # Finalmente, se escala y desplaza la distribución para que coincida con
    # la media y desviación estándar deseadas.
    y_normalized = target_mean + target_std * z
    
    return np.clip(y_normalized, 0, 1)

# =============================================================================
# SECCIÓN 2: FILTRADO POR CONVOLUCIÓN (NUEVO PARA TP4)
# =============================================================================

def convolve2d(image, kernel):
    """
    Aplica convolución 2D a una imagen en escala de grises.
    Maneja los bordes replicando los píxeles del borde (zero-padding).
    """
    k_h, k_w = kernel.shape
    pad_h, pad_w = k_h // 2, k_w // 2
    
    # Añadir padding replicando los bordes
    padded_image = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='edge')
    
    output = np.zeros_like(image, dtype=np.float64)
    
    # Rotar el kernel 180 grados para la convolución
    kernel_flipped = np.flipud(np.fliplr(kernel))
    
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            region = padded_image[i:i + k_h, j:j + k_w]
            output[i, j] = np.sum(region * kernel_flipped)
            
    return output

# --- Generadores de Kernels ---

def get_kernel(filter_name):
    """Devuelve el kernel correspondiente al nombre del filtro."""
    
    # --- PASABAJOS ---
    if filter_name == "Plano 3x3":
        return np.ones((3, 3)) / 9
    if filter_name == "Plano 5x5":
        return np.ones((5, 5)) / 25
    if filter_name == "Plano 7x7":
        return np.ones((7, 7)) / 49
        
    if filter_name == "Bartlett 3x3":
        k = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]])
        return k / k.sum()
    if filter_name == "Bartlett 5x5":
        k = np.array([1, 2, 3, 2, 1])
        k = np.outer(k, k)
        return k / k.sum()
    if filter_name == "Bartlett 7x7":
        k = np.array([1, 2, 3, 4, 3, 2, 1])
        k = np.outer(k, k)
        return k / k.sum()
        
    if filter_name == "Gaussiano 5x5":
        k = np.array([1, 4, 6, 4, 1])
        k = np.outer(k, k)
        return k / k.sum()
    if filter_name == "Gaussiano 7x7":
        k = np.array([1, 6, 15, 20, 15, 6, 1])
        k = np.outer(k, k)
        return k / k.sum()
        
    # --- DETECTORES DE BORDES ---
    if filter_name == "Laplaciano v4":
        return np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
    if filter_name == "Laplaciano v8":
        return np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        
    # Sobel
    sobel_base_v = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    if filter_name == "Sobel O (Oeste)": return sobel_base_v
    if filter_name == "Sobel E (Este)": return -sobel_base_v
    if filter_name == "Sobel N (Norte)": return sobel_base_v.T
    if filter_name == "Sobel S (Sur)": return -sobel_base_v.T
    if filter_name == "Sobel NO (Noroeste)": return np.array([[-2, -1, 0], [-1, 0, 1], [0, 1, 2]])
    if filter_name == "Sobel SE (Sudeste)": return -np.array([[-2, -1, 0], [-1, 0, 1], [0, 1, 2]])
    if filter_name == "Sobel NE (Noreste)": return np.array([[0, 1, 2], [-1, 0, 1], [-2, -1, 0]])
    if filter_name == "Sobel SO (Sudoeste)": return -np.array([[0, 1, 2], [-1, 0, 1], [-2, -1, 0]])
    
    # --- OTROS FILTROS ---
    if filter_name == "Pasaaltos (fc=0.2)":
        return np.identity(3) - (get_kernel("Pasabajos Plano 3x3") * 0.2) # Aproximación
    if filter_name == "Pasaaltos (fc=0.4)":
        return np.identity(3) - (get_kernel("Pasabajos Plano 3x3") * 0.4) # Aproximación

    if filter_name == "Pasabanda (DoG)":
        gauss5 = get_kernel("Gaussiano 5x5")
        # Para restar, necesitamos que Bartlett sea del mismo tamaño
        bartlett3 = get_kernel("Bartlett 3x3")
        bartlett5_padded = np.pad(bartlett3, pad_width=1, mode='constant', constant_values=0)
        return gauss5 - bartlett5_padded

    return np.array([[1]]) # Kernel identidad si no se encuentra

# =============================================================================
# SECCIÓN 3: PROCESAMIENTO MORFOLÓGICO (NUEVO PARA TP5)
# =============================================================================

def erosion(image, structure_size=3):
    """Aplica el filtro de erosión (mínimo local)."""
    structure = np.ones((structure_size, structure_size))
    return minimum_filter(image, footprint=structure)

def dilatacion(image, structure_size=3):
    """Aplica el filtro de dilatación (máximo local)."""
    structure = np.ones((structure_size, structure_size))
    return maximum_filter(image, footprint=structure)

def apertura(image, structure_size=3):
    """Aplica el filtro de apertura (erosión seguida de dilatación)."""
    eroded = erosion(image, structure_size)
    return dilatacion(eroded, structure_size)

def cierre(image, structure_size=3):
    """Aplica el filtro de cierre (dilatación seguida de erosión)."""
    dilated = dilatacion(image, structure_size)
    return erosion(dilated, structure_size)
    
def borde_morfologico(image, structure_size=3):
    """Calcula el borde morfológico (dilatación - erosión)."""
    dilated = dilatacion(image, structure_size)
    eroded = erosion(image, structure_size)
    return dilated - eroded

def mediana(image, structure_size=3):
    """Aplica el filtro de mediana."""
    return median_filter(image, size=structure_size)

