from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.core.processor import process, OPERATIONS

router = APIRouter(prefix="/api/v1/cv", tags=["image-processing"])

ALLOWED = {"jpg", "jpeg", "png", "bmp", "webp"}
ALL_OPS = list(OPERATIONS.keys()) + ["contours"]


def _validate(filename: str):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED:
        raise HTTPException(status_code=400, detail=f"Unsupported format: .{ext}")


@router.get("/operations")
def list_operations():
    return {"operations": ALL_OPS}


@router.post("/process")
async def process_image(
    file: UploadFile = File(...),
    operation: str = Form("canny"),
    threshold1: int = Form(100),
    threshold2: int = Form(200),
    ksize: int = Form(15),
    sigma: float = Form(3.0),
    block_size: int = Form(11),
    C: int = Form(2),
    iterations: int = Form(1),
    threshold: int = Form(127),
):
    _validate(file.filename)
    if operation not in ALL_OPS:
        raise HTTPException(status_code=400, detail=f"Unknown operation: {operation}. Choose from: {ALL_OPS}")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    params = {
        "threshold1": threshold1, "threshold2": threshold2,
        "ksize": ksize, "sigma": sigma,
        "block_size": block_size, "C": C,
        "iterations": iterations, "threshold": threshold,
    }
    try:
        return process(content, operation, params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
