from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health/live", tags=["System"])
async def liveness() -> dict[str, str]:
    """Process-level liveness probe; no external dependency is required."""
    return {"status": "ok"}


@router.get("/health/ready", tags=["System"])
async def readiness() -> dict[str, str]:
    """Application readiness probe."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/health", tags=["System"])
async def health() -> dict[str, str]:
    """Backward-compatible health endpoint."""
    return await readiness()
