import numpy as np

# --- CONSTANTES Y CONVERSIÓN ---

""" Matriz de conversión de RGB a YIQ """
MAT_YIQ = np.array([[0.299, 0.595716, 0.211456],
                    [0.587, -0.274453, -0.522591],
                    [0.114, -0.321263, 0.311135]])

def rgb2yiq(_im):
    """Convierte una imagen de RGB a YIQ de forma eficiente."""
    _rgb = _im.reshape((-1,3))
    _yiq = _rgb @ MAT_YIQ
    _yiq = _yiq.reshape(_im.shape)
    return _yiq

def yiq2rgb(_im):
    """Convierte una imagen de YIQ a RGB de forma eficiente."""
    _rgb = (_im.reshape((-1, 3)) @ np.linalg.inv(MAT_YIQ)).reshape(_im.shape)
    return np.clip(_rgb, 0, 1) # Buena práctica añadir clip aquí

# --- OPERACIONES ARITMÉTICAS ---

# --- Sumas ---
def sum_rgb_clampeada(im1, im2):
  """Suma directa y recorta el resultado si supera el rango [0, 1]."""
  return np.clip(im1 + im2, 0, 1)

def sum_rgb_promediada(im1, im2):
  """Suma las imágenes y las divide por 2 para obtener un promedio."""
  return (im1.astype(float) + im2.astype(float)) / 2.0

def sum_yiq_promediada(im1, im2):
    """Suma dos imágenes promediando sus valores en el espacio YIQ."""
    yiq1 = rgb2yiq(im1)
    yiq2 = rgb2yiq(im2)
    sum_y = (yiq1 + yiq2) / 2.0
    sum_r = yiq2rgb(sum_y)
    return sum_r # yiq2rgb ya hace el clip

# --- Diferencias ---
def diff_rgb_absoluta(im1, im2):
  """Calcula la diferencia absoluta (brillo) entre dos imágenes RGB."""
  return np.abs(im1 - im2)

def diff_rgb_promediada(im1, im2):
    """Calcula la diferencia normalizada. El gris (0.5) es 'sin diferencia'."""
    diff = (im1.astype(float) - im2.astype(float)) / 2.0 + 0.5
    return np.clip(diff, 0, 1)

def diff_yiq_promediada(im1, im2):
    """Calcula la diferencia de luminancia normalizada."""
    yiq1 = rgb2yiq(im1)
    yiq2 = rgb2yiq(im2)
    diff_y = (yiq1[:, :, 0] - yiq2[:, :, 0]) / 2.0 + 0.5
    diff_image = np.stack([diff_y, diff_y, diff_y], axis=-1)
    return np.clip(diff_image, 0, 1)

# --- FUNCIONES DE COMPOSICIÓN ---

def if_darker(im1, im2):
    """Crea una imagen nueva usando el píxel más oscuro de cada imagen."""
    yiq1 = rgb2yiq(im1)
    yiq2 = rgb2yiq(im2)
    mask = yiq1[:, :, 0] < yiq2[:, :, 0]
    return np.where(mask[..., np.newaxis], im1, im2)

def if_lighter(im1, im2):
    """Crea una imagen nueva usando el píxel más claro de cada imagen."""
    yiq1 = rgb2yiq(im1)
    yiq2 = rgb2yiq(im2)
    mask = yiq1[:, :, 0] > yiq2[:, :, 0]
    return np.where(mask[..., np.newaxis], im1, im2)

# --- OTRAS FUNCIONES ---
def rmse(im_1, im_2 = 0):
    return ((im_1 - im_2)**2).mean()**0.5

def change_intensity(_im, alpha=1, beta=1):
    """Change linearly luminance and intensity in yiq."""
    _yiq = rgb2yiq(_im) * np.array([alpha, beta, beta])[np.newaxis, np.newaxis, :]
    _rgb = yiq2rgb(_yiq)
    return _rgb

def _clip(_data, matrix = np.eye(3)):
    corners = np.array(np.meshgrid([0., 1.], [0., 1.], [0., 1.])).swapaxes(0,3).reshape((8, 3))
    _mapped = corners @ matrix
    _data[..., :] = np.clip(_data[..., :], np.min(_mapped, axis=0), np.max(_mapped, axis=0))
    return _data
