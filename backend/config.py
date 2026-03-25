from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings loaded exclusively from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── LLM ──────────────────────────────────────────────────────────────────
    ollama_base_url: str = "http://ollama:11434"
    model_name: str = "llama3.1:8b"
    vision_model: str = "llava:13b"

    # ── Embeddings ────────────────────────────────────────────────────────────
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    clip_model: str = "openai/clip-vit-base-patch32"

    # ── Vector Store ──────────────────────────────────────────────────────────
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection: str = "multimodal_rag"

    # ── Database ──────────────────────────────────────────────────────────────
    postgres_url: str = "postgresql+asyncpg://user:password@postgres:5432/ragdb"

    # ── Cache + Queue ─────────────────────────────────────────────────────────
    redis_url: str = "redis://redis:6379"
    rabbitmq_url: str = "amqp://user:password@rabbitmq:5672/"

    # ── Auth ──────────────────────────────────────────────────────────────────
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # ── Upload ────────────────────────────────────────────────────────────────
    max_upload_size_mb: int = 50
    allowed_extensions: str = "pdf,jpg,jpeg,png,webp"

    # ── Observability ─────────────────────────────────────────────────────────
    otel_exporter_otlp_endpoint: str = "http://otel-collector:4317"

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    rate_limit_per_minute: int = 60

    # ── Generation ────────────────────────────────────────────────────────────
    enable_chain_of_thought: bool = False

    @property
    def allowed_extensions_set(self) -> set[str]:
        return {ext.strip().lower() for ext in self.allowed_extensions.split(",")}

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
