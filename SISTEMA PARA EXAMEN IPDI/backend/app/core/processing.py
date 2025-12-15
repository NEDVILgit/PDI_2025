import numpy as np
import cv2
from typing import Tuple, List, Optional

def ensure_grayscale(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def ensure_color(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image

# --- Binarization ---
def apply_threshold(image: np.ndarray, threshold: int) -> np.ndarray:
    gray = ensure_grayscale(image)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return binary

def apply_invert(image: np.ndarray) -> np.ndarray:
    return cv2.bitwise_not(image)

# --- Morphology ---
def get_kernel(size: int) -> np.ndarray:
    return cv2.getStructuringElement(cv2.MORPH_RECT, (size, size))

def apply_morphology(image: np.ndarray, operation: str, size: int) -> np.ndarray:
    kernel = get_kernel(size)
    gray = ensure_grayscale(image)
    
    if operation == 'erosion':
        return cv2.erode(gray, kernel, iterations=1)
    elif operation == 'dilation':
        return cv2.dilate(gray, kernel, iterations=1)
    elif operation == 'opening':
        return cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    elif operation == 'closing':
        return cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    elif operation == 'boundary_external':
        dilation = cv2.dilate(gray, kernel, iterations=1)
        return cv2.subtract(dilation, gray)
    elif operation == 'boundary_internal':
        erosion = cv2.erode(gray, kernel, iterations=1)
        return cv2.subtract(gray, erosion)
    return image

# --- Convolution ---
def get_convolution_kernel(name: str, size: int = 3) -> np.ndarray:
    if name == 'flat':
        return np.ones((size, size), np.float32) / (size * size)
    elif name == 'bartlett':
        if size == 3:
            k = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], dtype=np.float32)
            return k / 16.0
        elif size == 5:
            k = np.array([
                [1, 2, 3, 2, 1],
                [2, 4, 6, 4, 2],
                [3, 6, 9, 6, 3],
                [2, 4, 6, 4, 2],
                [1, 2, 3, 2, 1]
            ], dtype=np.float32)
            return k / 81.0
        elif size == 7:
             # Simplified generation for 7x7 Bartlett (triangle * triangle)
            row = np.array([1, 2, 3, 4, 3, 2, 1], dtype=np.float32)
            k = np.outer(row, row)
            return k / np.sum(k)
            
    elif name == 'gaussian':
        # Sigma is roughly 0.3*((ksize-1)*0.5 - 1) + 0.8
        return cv2.getGaussianKernel(size, 0) @ cv2.getGaussianKernel(size, 0).T
        
    elif name == 'laplacian':
        if size == 4: # v4
            return np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]], dtype=np.float32)
        elif size == 8: # v8
            return np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], dtype=np.float32)
            
    elif name == 'sobel':
        # Handled separately usually, but can define kernels
        pass
        
    return np.eye(size, dtype=np.float32)

def apply_convolution(image: np.ndarray, kernel_name: str, size: int = 3, direction: str = None) -> np.ndarray:
    # Operations usually applied on channel 1 (Luminance) or Grayscale
    gray = ensure_grayscale(image)
    
    if kernel_name == 'sobel':
        if direction == 'north':
            k = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
        elif direction == 'south':
            k = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], dtype=np.float32)
        elif direction == 'east':
            k = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
        elif direction == 'west':
            k = np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]], dtype=np.float32)
        elif direction == 'northeast':
            k = np.array([[0, -1, -2], [1, 0, -1], [2, 1, 0]], dtype=np.float32)
        elif direction == 'southeast':
            k = np.array([[-2, -1, 0], [-1, 0, 1], [0, 1, 2]], dtype=np.float32)
        elif direction == 'northwest':
            k = np.array([[0, 1, 2], [-1, 0, 1], [-2, -1, 0]], dtype=np.float32)
        elif direction == 'southwest':
            k = np.array([[2, 1, 0], [1, 0, -1], [0, -1, -2]], dtype=np.float32)
        else:
             return gray
        return cv2.filter2D(gray, -1, k)
        
    kernel = get_convolution_kernel(kernel_name, size)
    return cv2.filter2D(gray, -1, kernel)

# --- Luminance ---
def apply_luminance(image: np.ndarray, operation: str, **kwargs) -> np.ndarray:
    # Usually applied on grayscale or V channel, here we assume grayscale input for simplicity or convert
    gray = ensure_grayscale(image).astype(np.float32)
    
    if operation == 'sqrt':
        res = np.sqrt(gray) * (255.0 / np.sqrt(255.0))
    elif operation == 'square':
        res = np.square(gray) * (255.0 / (255.0**2))
    elif operation == 'linear':
        # Piecewise linear: y = mx + c logic
        # Expects points list [(x1, y1), (x2, y2)...]
        # Simplified: just contrast stretching or specific points
        # For this task, let's implement a simple contrast stretch or look-up table if points provided
        # User request says "Lineal a Trozos" (Piecewise Linear)
        # We need points. Let's assume a standard contrast stretch if no points, 
        # or specific points if provided.
        # Let's implement a generic LUT based on points (0,0) -> (x1, y1) -> (x2, y2) -> (255, 255)
        points = kwargs.get('points', [])
        if not points:
            return image
        
        lut = np.zeros(256, dtype=np.uint8)
        x_prev, y_prev = 0, 0
        
        # Sort points by x
        points.sort(key=lambda p: p[0])
        
        # Add (255, 255) if not present to close the loop
        if points[-1][0] < 255:
            points.append((255, 255))
            
        for x, y in points:
            slope = (y - y_prev) / (x - x_prev + 1e-5)
            for i in range(int(x_prev), int(x) + 1):
                if i < 256:
                    val = y_prev + slope * (i - x_prev)
                    lut[i] = np.clip(val, 0, 255)
            x_prev, y_prev = x, y
            
        return cv2.LUT(ensure_grayscale(image), lut)

    else:
        return image
        
    return np.clip(res, 0, 255).astype(np.uint8)

# --- Arithmetic ---
def apply_arithmetic(img1: np.ndarray, img2: np.ndarray, operation: str) -> np.ndarray:
    # Ensure same size
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    
    # Convert to float for calculations
    i1 = img1.astype(np.float32)
    i2 = img2.astype(np.float32)
    
    if operation == 'add_avg':
        res = (i1 + i2) / 2
    elif operation == 'add_clamp':
        res = i1 + i2
    elif operation == 'sub_avg':
        res = (i1 - i2) / 2 # Can be negative, need to handle? Usually absolute or shift. 
        # "Resta promediada" often implies (A - B + 255)/2 or similar to keep in range.
        # Or just (A-B)/2. Let's assume simple average difference.
        res = (i1 - i2) # If negative, clip? 
        # Let's stick to standard: (A-B) clipped 0-255
        # "Promediada" might mean (A-B)/2 + 128?
        # Let's do (A-B) and clip for now, or check standard IPDI definition.
        # Usually "Resta" is |A-B| or A-B+128.
        # Let's implement A - B and clip.
        res = i1 - i2
    elif operation == 'sub_clamp':
        res = i1 - i2
    else:
        return img1

    return np.clip(res, 0, 255).astype(np.uint8)

# --- Chromatic ---
def rgb_to_yiq(image: np.ndarray) -> np.ndarray:
    # OpenCV doesn't have direct BGR2YIQ, need custom matrix
    # Y = 0.299R + 0.587G + 0.114B
    # I = 0.596R - 0.274G - 0.322B
    # Q = 0.211R - 0.523G + 0.312B
    # Input is BGR from OpenCV
    image = image.astype(np.float32) / 255.0
    B, G, R = cv2.split(image)
    
    Y = 0.299*R + 0.587*G + 0.114*B
    I = 0.596*R - 0.274*G - 0.322*B
    Q = 0.211*R - 0.523*G + 0.312*B
    
    # Normalize to 0-1 for display or keep as float? 
    # Usually Y is 0-1, I and Q are -0.5 to 0.5 roughly.
    # To display, we might need to shift/scale.
    # But for "Conversion", returning the raw values (or mapped to 0-255) is key.
    # Let's map to 3 channel image for visualization if needed, 
    # but the user might want the raw data. 
    # For visualization purposes in the UI, we usually map I and Q to visible range.
    # Let's return a 3-channel float image.
    return cv2.merge([Y, I, Q])

def yiq_to_rgb(image: np.ndarray) -> np.ndarray:
    # Inverse
    # R = Y + 0.956I + 0.621Q
    # G = Y - 0.272I - 0.647Q
    # B = Y - 1.106I + 1.703Q
    Y, I, Q = cv2.split(image)
    
    R = Y + 0.956*I + 0.621*Q
    G = Y - 0.272*I - 0.647*Q
    B = Y - 1.106*I + 1.703*Q
    
    rgb = cv2.merge([B, G, R]) # BGR order
    return np.clip(rgb * 255.0, 0, 255).astype(np.uint8)

def get_channel(image: np.ndarray, channel: int) -> np.ndarray:
    # 0=B, 1=G, 2=R
    if len(image.shape) < 3:
        return image
    c = cv2.split(image)[channel]
    return c

def avg_channels(image: np.ndarray) -> np.ndarray:
    if len(image.shape) < 3:
        return image
    return np.mean(image, axis=2).astype(np.uint8)

# --- Histogram ---
def calculate_histogram(image: np.ndarray) -> dict:
    # Calculate histogram for each channel
    if len(image.shape) == 2:
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        return {"gray": hist.flatten().tolist()}
    else:
        hist_b = cv2.calcHist([image], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([image], [1], None, [256], [0, 256])
        hist_r = cv2.calcHist([image], [2], None, [256], [0, 256])
        return {
            "b": hist_b.flatten().tolist(),
            "g": hist_g.flatten().tolist(),
            "r": hist_r.flatten().tolist()
        }

def equalize_histogram(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 2:
        return cv2.equalizeHist(image)
    else:
        # Convert to YUV/YCrCb, equalize Y, convert back
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        ycrcb[:,:,0] = cv2.equalizeHist(ycrcb[:,:,0])
        return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
