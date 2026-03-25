from __future__ import annotations

from fastapi import APIRouter
from schemas.response import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", version="1.0.0")


@router.get("/metrics")
async def metrics() -> dict:
    """Expose basic metrics — OpenTelemetry collector handles full metrics."""
    return {"status": "metrics_exported_via_otlp"}
