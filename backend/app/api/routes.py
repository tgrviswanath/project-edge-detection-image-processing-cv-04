from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.core.service import process_image, get_operations
import httpx

router = APIRouter(prefix="/api/v1", tags=["image-processing"])


def _handle(e: Exception):
    if isinstance(e, httpx.ConnectError):
        raise HTTPException(status_code=503, detail="CV service unavailable")
    if isinstance(e, httpx.HTTPStatusError):
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    raise HTTPException(status_code=500, detail=str(e))


@router.get("/operations")
async def operations():
    try:
        return await get_operations()
    except Exception as e:
        _handle(e)


@router.post("/process")
async def process(
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
    try:
        content = await file.read()
        params = {
            "threshold1": threshold1, "threshold2": threshold2,
            "ksize": ksize, "sigma": sigma,
            "block_size": block_size, "C": C,
            "iterations": iterations, "threshold": threshold,
        }
        return await process_image(
            file.filename, content,
            file.content_type or "image/jpeg",
            operation, params,
        )
    except Exception as e:
        _handle(e)
