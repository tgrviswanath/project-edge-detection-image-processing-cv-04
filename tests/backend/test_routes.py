from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)

MOCK_RESULT = {
    "operation": "canny", "params": {"threshold1": 100, "threshold2": 200},
    "image_width": 200, "image_height": 200,
    "result_image": "base64string", "original_image": "base64string",
    "stats": {"mean": 45.2, "std": 30.1, "min": 0, "max": 255},
    "contour_count": None,
}
MOCK_OPS = {"operations": ["canny", "sobel", "blur", "grayscale"]}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


@patch("app.core.service.get_operations", new_callable=AsyncMock, return_value=MOCK_OPS)
def test_operations_endpoint(mock_ops):
    r = client.get("/api/v1/operations")
    assert r.status_code == 200
    assert "canny" in r.json()["operations"]


@patch("app.core.service.process_image", new_callable=AsyncMock, return_value=MOCK_RESULT)
def test_process_endpoint(mock_proc):
    r = client.post("/api/v1/process",
        files={"file": ("test.jpg", b"fake", "image/jpeg")},
        data={"operation": "canny"})
    assert r.status_code == 200
    assert r.json()["operation"] == "canny"
