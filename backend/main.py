from __future__ import annotations

import logging

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from observability.tracing import setup_tracing
from observability.metrics import setup_metrics
from auth.middleware import JWTMiddleware
from storage.postgres_client import init_db
from api.v1 import routes_upload, routes_chat, routes_index, routes_health

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting Multimodal RAG backend …")
    await init_db()
    setup_tracing(settings.otel_exporter_otlp_endpoint)
    setup_metrics()
    yield
    logger.info("Shutting down Multimodal RAG backend …")


app = FastAPI(
    title="Multimodal RAG API",
    version="1.0.0",
    description="Production-grade Multimodal RAG system — 100% open source",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── JWT middleware (applied to all /api/v1/ routes in the middleware itself) ──
app.add_middleware(JWTMiddleware)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(routes_health.router, prefix="/api/v1")
app.include_router(routes_upload.router, prefix="/api/v1")
app.include_router(routes_index.router, prefix="/api/v1")
app.include_router(routes_chat.router, prefix="/api/v1")
