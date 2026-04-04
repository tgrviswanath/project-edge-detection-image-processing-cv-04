# Project CV-04 - Edge Detection & Image Processing

Microservice CV system that applies 10 classic OpenCV image processing operations with real-time before/after comparison.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND  (React - Port 3000)                              │
│  axios POST /api/v1/process                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP JSON
┌──────────────────────▼──────────────────────────────────────┐
│  BACKEND  (FastAPI - Port 8000)                             │
│  httpx POST /api/v1/cv/process  →  calls cv-service         │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP JSON
┌──────────────────────▼──────────────────────────────────────┐
│  CV SERVICE  (FastAPI - Port 8001)                          │
│  OpenCV applies selected operation                          │
│  Returns { original_image, processed_image, operation }     │
└─────────────────────────────────────────────────────────────┘
```

---

## 10 Supported Operations

| Operation | Algorithm | What it does |
|-----------|-----------|--------------|
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

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Frontend | React, MUI |
| Backend | FastAPI, httpx |
| CV | OpenCV, NumPy, Pillow |
| Deployment | Docker, docker-compose |

---

## Prerequisites

- Python 3.12+
- Node.js — run `nvs use 20.14.0` before starting the frontend

---

## Local Run

### Step 1 — Start CV Service (Terminal 1)

```bash
cd cv-service
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Verify: http://localhost:8001/health → `{"status":"ok"}`

### Step 2 — Start Backend (Terminal 2)

```bash
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Step 3 — Start Frontend (Terminal 3)

```bash
cd frontend
npm install && npm start
```

Opens at: http://localhost:3000

---

## Environment Files

### `backend/.env`

```
APP_NAME=Image Processing API
APP_VERSION=1.0.0
ALLOWED_ORIGINS=["http://localhost:3000"]
CV_SERVICE_URL=http://localhost:8001
```

### `frontend/.env`

```
REACT_APP_API_URL=http://localhost:8000
```

---

## Docker Run

```bash
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API docs | http://localhost:8000/docs |
| CV Service docs | http://localhost:8001/docs |

---

## Run Tests

```bash
cd cv-service && venv\Scripts\activate
pytest ../tests/cv-service/ -v

cd backend && venv\Scripts\activate
pytest ../tests/backend/ -v
```

---

## Project Structure

```
project-edge-detection-image-processing-cv-04/
├── frontend/                    ← React (Port 3000)
├── backend/                     ← FastAPI (Port 8000)
├── cv-service/                  ← FastAPI CV (Port 8001)
│   └── app/
│       ├── api/routes.py
│       ├── core/processor.py    ← 10 OpenCV operations
│       └── main.py
├── samples/
├── tests/
├── docker/
└── docker-compose.yml
```

---

## API Reference

```
POST /api/v1/process
Body:     { "image": "<base64>", "operation": "canny" }
Response: { "original_image": "<base64>", "processed_image": "<base64>", "operation": "canny" }
```
