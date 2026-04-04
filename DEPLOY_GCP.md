# GCP Deployment Guide — Project CV-04 Edge Detection & Image Processing

---

## GCP Services for Image Processing

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Cloud Vision API**                 | Image properties, safe search, and object detection alongside processing     | When you need managed image analysis               |
| **Cloud Functions**                  | Run OpenCV image processing operations serverlessly — no container needed    | When you want serverless image transformation      |
| **Vertex AI Gemini Vision**          | Gemini Pro Vision for intelligent image analysis guidance                    | When you need AI-guided image processing           |

> For classic CV operations (Canny, Sobel, blur, threshold), **Cloud Functions with OpenCV** is the most cost-effective option — pay only per invocation, no always-on containers needed.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Cloud Run**              | Run backend + cv-service containers — serverless, scales to zero    | Best match for your current microservice architecture |
| **Artifact Registry**      | Store your Docker images                                            | Used with Cloud Run or GKE                            |

### 3. Frontend Hosting

| Service                    | What it does                                                              |
|----------------------------|---------------------------------------------------------------------------| 
| **Firebase Hosting**       | Host your React frontend — free tier, auto CI/CD from GitHub              |

### 4. Supporting Services

| Service                        | Purpose                                                                   |
|--------------------------------|---------------------------------------------------------------------------|
| **Cloud Storage**              | Store uploaded images and processed results                               |
| **Secret Manager**             | Store API keys and connection strings instead of .env files               |
| **Cloud Monitoring + Logging** | Track processing latency, operation types, request volume                 |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Firebase Hosting — React Frontend                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Cloud Run — Backend (FastAPI :8000)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal HTTPS
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Cloud Run         │    │ Cloud Functions + OpenCV           │
│ CV Service :8001  │    │ Serverless image processing        │
│ OpenCV filters    │    │ Pay per invocation                 │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
gcloud auth login
gcloud projects create imgproc-cv-project --name="Image Processing"
gcloud config set project imgproc-cv-project
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com cloudfunctions.googleapis.com \
  storage.googleapis.com cloudbuild.googleapis.com
```

---

## Step 1 — Create Artifact Registry and Push Images

```bash
GCP_REGION=europe-west2
gcloud artifacts repositories create imgproc-repo \
  --repository-format=docker --location=$GCP_REGION
gcloud auth configure-docker $GCP_REGION-docker.pkg.dev
AR=$GCP_REGION-docker.pkg.dev/imgproc-cv-project/imgproc-repo
docker build -f docker/Dockerfile.cv-service -t $AR/cv-service:latest ./cv-service
docker push $AR/cv-service:latest
docker build -f docker/Dockerfile.backend -t $AR/backend:latest ./backend
docker push $AR/backend:latest
```

---

## Step 2 — Deploy to Cloud Run

```bash
gcloud run deploy cv-service \
  --image $AR/cv-service:latest --region $GCP_REGION \
  --port 8001 --no-allow-unauthenticated \
  --min-instances 1 --max-instances 3 --memory 2Gi --cpu 1

CV_URL=$(gcloud run services describe cv-service --region $GCP_REGION --format "value(status.url)")

gcloud run deploy backend \
  --image $AR/backend:latest --region $GCP_REGION \
  --port 8000 --allow-unauthenticated \
  --min-instances 1 --max-instances 5 --memory 1Gi --cpu 1 \
  --set-env-vars CV_SERVICE_URL=$CV_URL
```

---

## Option B — Use Cloud Functions with OpenCV

```python
# main.py (Cloud Function)
import functions_framework
import json, base64, cv2, numpy as np

@functions_framework.http
def process_image(request):
    body = request.get_json()
    image_bytes = base64.b64decode(body["image"])
    operation = body.get("operation", "canny")
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ops = {
        "canny": lambda: cv2.Canny(gray, 100, 200),
        "blur": lambda: cv2.GaussianBlur(img, (15, 15), 0),
        "grayscale": lambda: gray,
        "threshold": lambda: cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2),
        "sobel": lambda: cv2.Sobel(gray, cv2.CV_64F, 1, 1, ksize=5).astype(np.uint8)
    }
    result = ops.get(operation, ops["canny"])()
    _, buffer = cv2.imencode(".jpg", result)
    return json.dumps({"processed_image": base64.b64encode(buffer.tobytes()).decode()})
```

Deploy:
```bash
gcloud functions deploy process-image \
  --gen2 --runtime python311 --region $GCP_REGION \
  --source . --entry-point process_image \
  --trigger-http --allow-unauthenticated \
  --memory 512MB
```

---

## Estimated Monthly Cost

| Service                    | Tier                  | Est. Cost          |
|----------------------------|-----------------------|--------------------|
| Cloud Run (backend)        | 1 vCPU / 1 GB         | ~$10–15/month      |
| Cloud Run (cv-service)     | 1 vCPU / 2 GB         | ~$12–18/month      |
| Artifact Registry          | Storage               | ~$1–2/month        |
| Firebase Hosting           | Free tier             | $0                 |
| Cloud Functions            | 2M invocations free   | $0 (free tier)     |
| **Total (Option A)**       |                       | **~$23–35/month**  |
| **Total (Option B)**       |                       | **~$1–2/month**    |

For exact estimates → https://cloud.google.com/products/calculator

---

## Teardown

```bash
gcloud run services delete backend --region $GCP_REGION --quiet
gcloud run services delete cv-service --region $GCP_REGION --quiet
gcloud artifacts repositories delete imgproc-repo --location=$GCP_REGION --quiet
gcloud projects delete imgproc-cv-project
```
