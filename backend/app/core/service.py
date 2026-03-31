import httpx
from app.core.config import settings

CV_URL = settings.CV_SERVICE_URL


async def process_image(
    filename: str, content: bytes, content_type: str,
    operation: str, params: dict,
) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{CV_URL}/api/v1/cv/process",
            files={"file": (filename, content, content_type)},
            data={"operation": operation, **{k: str(v) for k, v in params.items()}},
            timeout=30.0,
        )
        r.raise_for_status()
        return r.json()


async def get_operations() -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{CV_URL}/api/v1/cv/operations", timeout=10.0)
        r.raise_for_status()
        return r.json()
