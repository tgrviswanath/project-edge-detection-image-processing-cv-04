# Project 04 - Edge Detection & Image Processing (CV)

Apply 10 classic OpenCV image processing operations with real-time before/after comparison.

## Architecture

```
Frontend :3000  →  Backend :8000  →  CV Service :8001
  React/MUI        FastAPI/httpx      FastAPI/OpenCV
```

## 10 Supported Operations

| Operation | Algorithm | What it does |
|---|---|---|
| `canny` | Canny edge detector | Finds edges using gradient thresholds |
| `sobel` | Sobel operator | Detects horizontal + vertical gradients |
| `laplacian` | Laplacian | Second-order derivative edge detection |
| `blur` | Gaussian blur | Smooths image to reduce noise |
| `sharpen` | Unsharp masking | Enhances edges and fine details |
| `threshold` | Adaptive threshold | Binarizes image handling uneven lighting |
| `dilate` | Morphological dilation | Expands bright regions |
| `erode` | Morphological erosion | Shrinks bright regions |
| `contours` | Contour detection | Finds and draws object boundaries |
| `grayscale` | Color conversion | Removes color information |

## What's Different from Projects 01-03

| | Project 01 | Project 02 | Project 03 | Project 04 |
|---|---|---|---|---|
| Task | Classify | Detect faces | Extract text | Transform image |
| Model | SVM | DNN SSD | Tesseract | Classic CV algorithms |
| Output | Label | Boxes | Text | Processed image |
| New concept | sklearn | DNN inference | OCR | OpenCV filters |

## Local Run

```bash
# Terminal 1 - CV Service
cd cv-service && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# Terminal 2 - Backend
cd backend && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 3 - Frontend
cd frontend && npm install && npm start
```

- CV Service docs: http://localhost:8001/docs
- Backend docs:   http://localhost:8000/docs
- UI:             http://localhost:3000

## Docker

```bash
docker-compose up --build
```
