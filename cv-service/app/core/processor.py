"""
OpenCV image processing pipeline.
Supports 10 operations:
  canny        - Canny edge detection
  sobel        - Sobel gradient (X+Y combined)
  laplacian    - Laplacian edge detection
  blur         - Gaussian blur
  sharpen      - Unsharp masking
  threshold    - Adaptive threshold (binarization)
  dilate       - Morphological dilation
  erode        - Morphological erosion
  contours     - Contour detection + drawing
  grayscale    - Convert to grayscale
"""
import cv2
import numpy as np
from PIL import Image
import io
import base64
from app.core.config import settings


def _load(image_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    if max(w, h) > settings.MAX_IMAGE_SIZE:
        scale = settings.MAX_IMAGE_SIZE / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def _to_base64(img: np.ndarray) -> str:
    # Convert grayscale to BGR for consistent encoding
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return base64.b64encode(buf).decode("utf-8")


def _stats(img: np.ndarray) -> dict:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    return {
        "mean": round(float(np.mean(gray)), 2),
        "std": round(float(np.std(gray)), 2),
        "min": int(np.min(gray)),
        "max": int(np.max(gray)),
    }


OPERATIONS = {
    "canny": lambda img, p: cv2.Canny(
        cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
        p.get("threshold1", 100), p.get("threshold2", 200)
    ),
    "sobel": lambda img, p: cv2.convertScaleAbs(
        cv2.Sobel(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F, 1, 0, ksize=3) +
        cv2.Sobel(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F, 0, 1, ksize=3)
    ),
    "laplacian": lambda img, p: cv2.convertScaleAbs(
        cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F)
    ),
    "blur": lambda img, p: cv2.GaussianBlur(
        img, (p.get("ksize", 15), p.get("ksize", 15)), 0
    ),
    "sharpen": lambda img, p: cv2.addWeighted(
        img, 1.5,
        cv2.GaussianBlur(img, (0, 0), p.get("sigma", 3)),
        -0.5, 0
    ),
    "threshold": lambda img, p: cv2.adaptiveThreshold(
        cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
        p.get("block_size", 11), p.get("C", 2)
    ),
    "dilate": lambda img, p: cv2.dilate(
        img,
        np.ones((p.get("ksize", 5), p.get("ksize", 5)), np.uint8),
        iterations=p.get("iterations", 1)
    ),
    "erode": lambda img, p: cv2.erode(
        img,
        np.ones((p.get("ksize", 5), p.get("ksize", 5)), np.uint8),
        iterations=p.get("iterations", 1)
    ),
    "grayscale": lambda img, p: cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
}


def _contours(img: np.ndarray, params: dict) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, params.get("threshold", 127), 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = img.copy()
    cv2.drawContours(result, contours, -1, (0, 255, 0), 2)
    return result, len(contours)


def process(image_bytes: bytes, operation: str, params: dict) -> dict:
    img = _load(image_bytes)
    h, w = img.shape[:2]
    contour_count = None

    if operation == "contours":
        result, contour_count = _contours(img, params)
    elif operation in OPERATIONS:
        result = OPERATIONS[operation](img, params)
    else:
        raise ValueError(f"Unknown operation: {operation}")

    return {
        "operation": operation,
        "params": params,
        "image_width": w,
        "image_height": h,
        "result_image": _to_base64(result),
        "original_image": _to_base64(img),
        "stats": _stats(result),
        "contour_count": contour_count,
    }
