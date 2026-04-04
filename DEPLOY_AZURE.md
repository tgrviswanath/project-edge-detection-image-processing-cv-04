# Azure Deployment Guide — Project CV-04 Edge Detection & Image Processing

---

## Azure Services for Image Processing

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Azure AI Vision**                  | Image enhancement, smart cropping, and thumbnail generation                  | When you need managed image transformation         |
| **Azure Functions**                  | Run OpenCV image processing operations serverlessly — no container needed    | When you want serverless image transformation      |
| **Azure OpenAI Vision**              | GPT-4V for intelligent image analysis and transformation guidance            | When you need AI-guided image processing           |

> For classic CV operations (Canny, Sobel, blur, threshold), **Azure Functions with OpenCV** is the most cost-effective option — pay only per invocation, no always-on containers needed.

### 2. Host Your Own Model (Keep Current Stack)

| Service                        | What it does                                                        | When to use                                           |
|--------------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Azure Container Apps**       | Run your 3 Docker containers (frontend, backend, cv-service)        | Best match for your current microservice architecture |
| **Azure Container Registry**   | Store your Docker images                                            | Used with Container Apps or AKS                       |

### 3. Frontend Hosting

| Service                   | What it does                                                               |
|---------------------------|----------------------------------------------------------------------------|
| **Azure Static Web Apps** | Host your React frontend — free tier available, auto CI/CD from GitHub     |

### 4. Supporting Services

| Service                       | Purpose                                                                  |
|-------------------------------|--------------------------------------------------------------------------|
| **Azure Blob Storage**        | Store uploaded images and processed results                              |
| **Azure Key Vault**           | Store API keys and connection strings instead of .env files              |
| **Azure Monitor + App Insights** | Track processing latency, operation types, request volume            |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Azure Static Web Apps — React Frontend                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Azure Container Apps — Backend (FastAPI :8000)             │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Container Apps    │    │ Azure Functions + OpenCV           │
│ CV Service :8001  │    │ Serverless image processing        │
│ OpenCV filters    │    │ Pay per invocation                 │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
az login
az group create --name rg-img-processing --location uksouth
az extension add --name containerapp --upgrade
```

---

## Step 1 — Create Container Registry and Push Images

```bash
az acr create --resource-group rg-img-processing --name imgprocacr --sku Basic --admin-enabled true
az acr login --name imgprocacr
ACR=imgprocacr.azurecr.io
docker build -f docker/Dockerfile.cv-service -t $ACR/cv-service:latest ./cv-service
docker push $ACR/cv-service:latest
docker build -f docker/Dockerfile.backend -t $ACR/backend:latest ./backend
docker push $ACR/backend:latest
```

---

## Step 2 — Deploy Container Apps

```bash
az containerapp env create --name imgproc-env --resource-group rg-img-processing --location uksouth

az containerapp create \
  --name cv-service --resource-group rg-img-processing \
  --environment imgproc-env --image $ACR/cv-service:latest \
  --registry-server $ACR --target-port 8001 --ingress internal \
  --min-replicas 1 --max-replicas 3 --cpu 1 --memory 2.0Gi

az containerapp create \
  --name backend --resource-group rg-img-processing \
  --environment imgproc-env --image $ACR/backend:latest \
  --registry-server $ACR --target-port 8000 --ingress external \
  --min-replicas 1 --max-replicas 5 --cpu 0.5 --memory 1.0Gi \
  --env-vars CV_SERVICE_URL=http://cv-service:8001
```

---

## Option B — Use Azure Functions with OpenCV

```python
# function_app.py
import azure.functions as func
import json, base64, cv2, numpy as np

app = func.FunctionApp()

@app.route(route="process", methods=["POST"])
def process_image(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()
    image_bytes = base64.b64decode(body["image"])
    operation = body.get("operation", "canny")
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ops = {
        "canny": lambda: cv2.Canny(gray, 100, 200),
        "blur": lambda: cv2.GaussianBlur(img, (15, 15), 0),
        "grayscale": lambda: gray,
        "threshold": lambda: cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    }
    result = ops.get(operation, ops["canny"])()
    _, buffer = cv2.imencode(".jpg", result)
    return func.HttpResponse(
        json.dumps({"processed_image": base64.b64encode(buffer.tobytes()).decode()}),
        mimetype="application/json"
    )
```

---

## Estimated Monthly Cost

| Service                  | Tier      | Est. Cost         |
|--------------------------|-----------|-------------------|
| Container Apps (backend) | 0.5 vCPU  | ~$10–15/month     |
| Container Apps (cv-svc)  | 1 vCPU    | ~$15–20/month     |
| Container Registry       | Basic     | ~$5/month         |
| Static Web Apps          | Free      | $0                |
| Azure Functions          | 1M free   | $0 (free tier)    |
| **Total (Option A)**     |           | **~$30–40/month** |
| **Total (Option B)**     |           | **~$5–10/month**  |

For exact estimates → https://calculator.azure.com

---

## Teardown

```bash
az group delete --name rg-img-processing --yes --no-wait
```
