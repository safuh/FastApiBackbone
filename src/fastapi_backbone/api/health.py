"""Operational health endpoints."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str


@router.get("/live", response_model=HealthResponse)
async def live(request: Request) -> HealthResponse:
    """Process-level liveness check with no dependency probing."""
    settings = request.app.state.settings
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/ready", response_model=HealthResponse)
async def ready(request: Request) -> HealthResponse:
    """Readiness endpoint; dependency checks belong to the consuming service."""
    settings = request.app.state.settings
    return HealthResponse(
        status="ready",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    """Human-friendly health endpoint."""
    return await live(request)
