# AWS Deployment Guide — Project CV-04 Edge Detection & Image Processing

---

## AWS Services for Image Processing

### 1. Ready-to-Use AI (No Model Needed)

| Service                    | What it does                                                                 | When to use                                        |
|----------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Amazon Rekognition**     | Image enhancement and analysis — detect objects, scenes, and image quality   | When you need managed image analysis alongside processing |
| **AWS Lambda**             | Run OpenCV image processing operations serverlessly — no container needed    | When you want serverless image transformation      |
| **Amazon Bedrock**         | Claude Vision for intelligent image analysis and transformation guidance     | When you need AI-guided image processing           |

> For classic CV operations (Canny, Sobel, blur, threshold), **AWS Lambda with OpenCV layer** is the most cost-effective option — pay only per invocation, no always-on containers needed.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **AWS App Runner**         | Run backend container — simplest, no VPC or cluster needed          | Quickest path to production                           |
| **Amazon ECS Fargate**     | Run backend + cv-service containers in a private VPC                | Best match for your current microservice architecture |
| **Amazon ECR**             | Store your Docker images                                            | Used with App Runner, ECS, or EKS                     |

### 3. Frontend Hosting

| Service               | What it does                                                                  |
|-----------------------|-------------------------------------------------------------------------------|
| **Amazon S3**         | Host your React build as a static website                                     |
| **Amazon CloudFront** | CDN in front of S3 — HTTPS, low latency globally                              |

### 4. Supporting Services

| Service                  | Purpose                                                                   |
|--------------------------|---------------------------------------------------------------------------|
| **Amazon S3**            | Store uploaded images and processed results                               |
| **AWS Secrets Manager**  | Store API keys and connection strings instead of .env files               |
| **Amazon CloudWatch**    | Track processing latency, operation types, request volume                 |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  S3 + CloudFront — React Frontend                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  AWS App Runner / ECS Fargate — Backend (FastAPI :8000)     │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ ECS Fargate       │    │ AWS Lambda + OpenCV Layer          │
│ CV Service :8001  │    │ Serverless image processing        │
│ OpenCV filters    │    │ Pay per invocation                 │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
aws configure
AWS_REGION=eu-west-2
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
```

---

## Step 1 — Create ECR and Push Images

```bash
aws ecr create-repository --repository-name imgproc/cv-service --region $AWS_REGION
aws ecr create-repository --repository-name imgproc/backend --region $AWS_REGION
ECR=$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR
docker build -f docker/Dockerfile.cv-service -t $ECR/imgproc/cv-service:latest ./cv-service
docker push $ECR/imgproc/cv-service:latest
docker build -f docker/Dockerfile.backend -t $ECR/imgproc/backend:latest ./backend
docker push $ECR/imgproc/backend:latest
```

---

## Step 2 — Deploy with App Runner

```bash
aws apprunner create-service \
  --service-name imgproc-backend \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ECR'/imgproc/backend:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "CV_SERVICE_URL": "http://cv-service:8001"
        }
      }
    }
  }' \
  --instance-configuration '{"Cpu": "1 vCPU", "Memory": "2 GB"}' \
  --region $AWS_REGION
```

---

## Option B — Use AWS Lambda with OpenCV Layer

```python
# lambda_function.py
import json, base64, cv2, numpy as np

def apply_operation(image_bytes: bytes, operation: str) -> bytes:
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
    return buffer.tobytes()

def lambda_handler(event, context):
    body = json.loads(event["body"])
    image_bytes = base64.b64decode(body["image"])
    operation = body.get("operation", "canny")
    result = apply_operation(image_bytes, operation)
    return {
        "statusCode": 200,
        "body": json.dumps({"processed_image": base64.b64encode(result).decode()})
    }
```

---

## Estimated Monthly Cost

| Service                    | Tier              | Est. Cost          |
|----------------------------|-------------------|--------------------|
| App Runner (backend)       | 1 vCPU / 2 GB     | ~$20–25/month      |
| App Runner (cv-service)    | 1 vCPU / 2 GB     | ~$20–25/month      |
| ECR + S3 + CloudFront      | Standard          | ~$3–7/month        |
| AWS Lambda                 | 1M requests free  | $0 (free tier)     |
| **Total (Option A)**       |                   | **~$43–57/month**  |
| **Total (Option B)**       |                   | **~$3–7/month**    |

For exact estimates → https://calculator.aws

---

## Teardown

```bash
aws ecr delete-repository --repository-name imgproc/backend --force
aws ecr delete-repository --repository-name imgproc/cv-service --force
```
