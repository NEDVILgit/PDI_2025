from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
import numpy as np
import cv2
import io
import json
from typing import List, Optional
from app.core import processing

app = FastAPI(title="IPDI Image Processing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helpers ---
async def read_image(file: UploadFile) -> np.ndarray:
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file")
    return img

def encode_image(image: np.ndarray) -> bytes:
    success, encoded_image = cv2.imencode('.png', image)
    if not success:
        raise HTTPException(status_code=500, detail="Could not encode image")
    return encoded_image.tobytes()

@app.get("/")
def read_root():
    return {"message": "IPDI API is running"}

# --- Endpoints ---

@app.post("/process/binarize")
async def binarize(
    file: UploadFile = File(...),
    threshold: int = Form(128),
    invert: bool = Form(False)
):
    image = await read_image(file)
    processed = processing.apply_threshold(image, threshold)
    if invert:
        processed = processing.apply_invert(processed)
    return Response(content=encode_image(processed), media_type="image/png")

@app.post("/process/morphology")
async def morphology(
    file: UploadFile = File(...),
    operation: str = Form(...),
    size: int = Form(3)
):
    image = await read_image(file)
    processed = processing.apply_morphology(image, operation, size)
    return Response(content=encode_image(processed), media_type="image/png")

@app.post("/process/convolution")
async def convolution(
    file: UploadFile = File(...),
    kernel: str = Form(...),
    size: int = Form(3),
    direction: Optional[str] = Form(None)
):
    image = await read_image(file)
    processed = processing.apply_convolution(image, kernel, size, direction)
    return Response(content=encode_image(processed), media_type="image/png")

@app.post("/process/luminance")
async def luminance(
    file: UploadFile = File(...),
    operation: str = Form(...),
    points: Optional[str] = Form(None) # JSON string for points
):
    image = await read_image(file)
    kwargs = {}
    if points:
        try:
            kwargs['points'] = json.loads(points)
        except:
            pass
            
    processed = processing.apply_luminance(image, operation, **kwargs)
    return Response(content=encode_image(processed), media_type="image/png")

@app.post("/process/arithmetic")
async def arithmetic(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    operation: str = Form(...)
):
    img1 = await read_image(file1)
    img2 = await read_image(file2)
    processed = processing.apply_arithmetic(img1, img2, operation)
    return Response(content=encode_image(processed), media_type="image/png")

@app.post("/process/chromatic")
async def chromatic(
    file: UploadFile = File(...),
    operation: str = Form(...), # rgb_to_yiq, yiq_to_rgb, avg, channel
    channel: Optional[int] = Form(None)
):
    image = await read_image(file)
    
    if operation == 'rgb_to_yiq':
        # Returns float image, need to visualize or return raw?
        # For visualization, we might want to normalize or just return as PNG (which clips)
        # But usually YIQ is for processing. 
        # Let's return a visualization where Y, I, Q are mapped to RGB channels?
        # Or just return the raw bytes? PNG is 8-bit usually.
        # If we want to show it, we probably want to visualize it.
        # Let's stick to returning a visualizable PNG.
        res = processing.rgb_to_yiq(image)
        # Map to 0-255 for display
        # Y is 0-1, I is -0.6 to 0.6, Q is -0.5 to 0.5
        # Simple visualization: Scale to 0-255
        # This is tricky. The user prompt shows "RGB -> YIQ" and a result.
        # Let's assumes standard conversion for display if needed, or just return the data.
        # If the frontend needs to display it, we should probably return a standard image.
        # Let's return the 3-channel image scaled to 0-255.
        # But wait, YIQ to RGB is also requested.
        # If we convert RGB->YIQ, we get a YIQ image. If we save it as PNG, it loses precision.
        # For this assignment, likely we just want to see the channels or the result.
        # Let's just return the result as is, clipped to 0-255 (which might look weird for I/Q but is standard for simple display).
        # Actually, let's normalize I and Q for display if it's just for viewing.
        # But if it's for further processing (like arithmetic on YIQ), we need the raw data.
        # The prompt implies "Conversiones RGB --> YIQ".
        # Let's just return the raw values clipped.
        res = np.clip(res * 255, 0, 255).astype(np.uint8)
        return Response(content=encode_image(res), media_type="image/png")
        
    elif operation == 'yiq_to_rgb':
        # Input is assumed to be YIQ (but uploaded as PNG, so 0-255).
        # We need to treat the input image as YIQ data.
        # So we normalize back to float.
        img_float = image.astype(np.float32) / 255.0
        res = processing.yiq_to_rgb(img_float)
        return Response(content=encode_image(res), media_type="image/png")
        
    elif operation == 'avg':
        res = processing.avg_channels(image)
        return Response(content=encode_image(res), media_type="image/png")
        
    elif operation == 'channel':
        if channel is not None:
            res = processing.get_channel(image, channel)
            return Response(content=encode_image(res), media_type="image/png")
            
    return Response(content=encode_image(image), media_type="image/png")

@app.post("/process/histogram")
async def histogram(
    file: UploadFile = File(...),
    equalize: bool = Form(False)
):
    image = await read_image(file)
    
    if equalize:
        image = processing.equalize_histogram(image)
        # Return both image and histogram? 
        # The prompt implies "Análisis y ecualización".
        # If equalized, we probably want to see the result image AND its new histogram.
        # But this endpoint structure is tricky.
        # Let's have a separate endpoint for equalization that returns the image,
        # and this one just returns the histogram data.
        # OR, we return a JSON with histogram data, and if equalized, we return the histogram of the equalized image.
        # But the user probably wants to SEE the equalized image too.
        # Let's split: /process/histogram (returns JSON), /process/equalize (returns Image).
        pass

    hist = processing.calculate_histogram(image)
    return JSONResponse(content=hist)

@app.post("/process/equalize")
async def equalize(file: UploadFile = File(...)):
    image = await read_image(file)
    processed = processing.equalize_histogram(image)
    return Response(content=encode_image(processed), media_type="image/png")
