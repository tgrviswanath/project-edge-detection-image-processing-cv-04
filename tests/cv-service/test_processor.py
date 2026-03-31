from fastapi.testclient import TestClient
from PIL import Image
import io
from app.main import app

client = TestClient(app)


def _sample_image() -> bytes:
    img = Image.new("RGB", (200, 200), color=(128, 64, 32))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


def test_list_operations():
    r = client.get("/api/v1/cv/operations")
    assert r.status_code == 200
    assert "operations" in r.json()
    assert "canny" in r.json()["operations"]


def test_canny():
    r = client.post("/api/v1/cv/process",
        files={"file": ("test.jpg", _sample_image(), "image/jpeg")},
        data={"operation": "canny", "threshold1": "100", "threshold2": "200"})
    assert r.status_code == 200
    data = r.json()
    assert data["operation"] == "canny"
    assert "result_image" in data
    assert "original_image" in data
    assert "stats" in data


def test_blur():
    r = client.post("/api/v1/cv/process",
        files={"file": ("test.jpg", _sample_image(), "image/jpeg")},
        data={"operation": "blur", "ksize": "15"})
    assert r.status_code == 200


def test_grayscale():
    r = client.post("/api/v1/cv/process",
        files={"file": ("test.jpg", _sample_image(), "image/jpeg")},
        data={"operation": "grayscale"})
    assert r.status_code == 200


def test_contours():
    r = client.post("/api/v1/cv/process",
        files={"file": ("test.jpg", _sample_image(), "image/jpeg")},
        data={"operation": "contours", "threshold": "127"})
    assert r.status_code == 200
    assert r.json()["contour_count"] is not None


def test_invalid_operation():
    r = client.post("/api/v1/cv/process",
        files={"file": ("test.jpg", _sample_image(), "image/jpeg")},
        data={"operation": "invalid_op"})
    assert r.status_code == 400


def test_unsupported_format():
    r = client.post("/api/v1/cv/process",
        files={"file": ("test.gif", b"GIF89a", "image/gif")},
        data={"operation": "canny"})
    assert r.status_code == 400
