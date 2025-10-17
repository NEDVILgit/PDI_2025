import numpy as np

MAT_YIQ = np.array([[0.299, 0.595716, 0.211456],
                    [0.587, -0.274453, -0.522591],
                    [0.114, -0.321263, 0.311135]])

def rgb2yiq(_im):
    _rgb = _im.reshape((-1,3))
    _yiq = _rgb @ MAT_YIQ
    _yiq = _yiq.reshape(_im.shape)
    return _yiq

def RGB_to_YIQ(rgb):
   yiq = np.zeros(rgb.shape)
   yiq[:,:,0] = 0.229*rgb[:,:,0] + 0.587*rgb[:,:,1] + 0.114*rgb[:,:,2]
   yiq[:,:,1] = 0.595716*rgb[:,:,0] - 0.274453*rgb[:,:,1] - 0.321263*rgb[:,:,2]
   yiq[:,:,2] = 0.211456*rgb[:,:,0] - 0.522591*rgb[:,:,1] + 0.311135*rgb[:,:,2]
   #yiq[:,:,3]=rgb[:,:,3]
   return yiq

def yiq2rgb(_im):
    return (_im.reshape((-1, 3)) @ np.linalg.inv(MAT_YIQ)).reshape(_im.shape)

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

def sum_rgb(im1, im2):
  return np.clip(im1 + im2, 0, 1)

def sum_rgb2(im1, im2):
  sum_r = im1[:, :, 0] + im2[:, :, 0]
  sum_g = im1[:, :, 1] + im2[:, :, 1]
  sum_b = im1[:, :, 2] + im2[:, :, 2]

  """
  Calcula la diferencia absoluta píxel a píxel entre dos imágenes RGB.
  Se asume que las imágenes de entrada están en formato de punto flotante en el rango [0, 1].
  El resultado también estará en el rango [0, 1].
  """
def diff_rgb(im1, im2):
  return np.abs(im1 - im2)

def sum_yiq(im1, im2):
    """
    Suma dos imágenes en el espacio YIQ y convierte el resultado a RGB.
    La suma se realiza en los tres canales YIQ, y el resultado final
    se recorta al rango válido de RGB [0, 1].
    """
    # Convertir ambas imágenes a YIQ usando tu función
    yiq1 = rgb2yiq(im1)
    yiq2 = rgb2yiq(im2)
    
    # Sumar las representaciones YIQ
    sum_y = yiq1 + yiq2
    
    # Convertir el resultado de vuelta a RGB
    sum_r = yiq2rgb(sum_y)
    
    # Recortar al rango válido de RGB y devolver
    return np.clip(sum_r, 0, 1)


    """
    Calcula la diferencia de luminancia (canal Y) entre dos imágenes.
    El resultado es una imagen en escala de grises que muestra dónde
    difieren en brillo las imágenes originales.
    """
def diff_yiq(im1, im2):
    # Convertir ambas imágenes a YIQ
    yiq1 = rgb2yiq(im1)
    yiq2 = rgb2yiq(im2)
    
    # Calcular la diferencia absoluta solo en el canal Y (luminancia)
    # yiq1[:, :, 0] es el canal Y de la primera imagen
    diff_y = np.abs(yiq1[:, :, 0] - yiq2[:, :, 0])
    
    # Crear una imagen en escala de grises repitiendo la diferencia
    # en los tres canales (R=G=B) para poder mostrarla con imshow
    diff_image = np.stack([diff_y, diff_y, diff_y], axis=-1)
    
    # Recortar por seguridad, aunque el resultado ya debería estar en [0, 1]
    return np.clip(diff_image, 0, 1)

def if_darker(im1, im2):
    """
    Compara dos imágenes y devuelve una nueva imagen que contiene, para
    cada posición, el píxel que sea más oscuro (menor luminancia).
    """
    # Convertir ambas imágenes a YIQ para obtener su luminancia
    yiq1 = rgb2yiq(im1)
    yiq2 = rgb2yiq(im2)
    
    # Obtener el canal de luminancia (Y) de cada imagen
    y1 = yiq1[:, :, 0]
    y2 = yiq2[:, :, 0]
    
    # Crear una máscara booleana. Será True donde im1 es más oscura que im2.
    mask = y1 < y2
    
    # Usar np.where para construir la imagen final.
    # Donde la máscara es True, se usa un píxel de im1.
    # Donde es False, se usa un píxel de im2.
    # np.newaxis expande la máscara para que coincida con las 3 dimensiones de color.
    return np.where(mask[..., np.newaxis], im1, im2)

def if_lighter(im1, im2):
    """
    Compara dos imágenes y devuelve una nueva imagen que contiene, para
    cada posición, el píxel que sea más claro (mayor luminancia).
    """
    # Convertir ambas imágenes a YIQ
    yiq1 = rgb2yiq(im1)
    yiq2 = rgb2yiq(im2)
    
    # Obtener el canal de luminancia (Y)
    y1 = yiq1[:, :, 0]
    y2 = yiq2[:, :, 0]
    
    # La máscara ahora es True donde im1 es más clara que im2
    mask = y1 > y2
    
    # La lógica es la misma que en if_darker, pero con la condición invertida
    return np.where(mask[..., np.newaxis], im1, im2)



