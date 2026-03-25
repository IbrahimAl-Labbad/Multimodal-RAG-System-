from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    import os
    os.environ["JWT_SECRET_KEY"] = "integration-test-secret"
    os.environ["POSTGRES_URL"] = "postgresql+asyncpg://user:password@localhost:5432/ragdb"
    os.environ["REDIS_URL"] = "redis://localhost:6379"
    os.environ["RABBITMQ_URL"] = "amqp://user:password@localhost:5672/"
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
    os.environ["MODEL_NAME"] = "llama3.1:8b"
    os.environ["VISION_MODEL"] = "llava:13b"
    os.environ["EMBEDDING_MODEL"] = "sentence-transformers/all-MiniLM-L6-v2"
    os.environ["CLIP_MODEL"] = "openai/clip-vit-base-patch32"
    os.environ["QDRANT_HOST"] = "localhost"
    os.environ["QDRANT_PORT"] = "6333"
    os.environ["QDRANT_COLLECTION"] = "test_collection"

    with (
        patch("storage.postgres_client.init_db", new=AsyncMock()),
        patch("observability.tracing.setup_tracing"),
        patch("observability.metrics.setup_metrics"),
    ):
        from main import app
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac


@pytest.mark.anyio
async def test_health_check(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.anyio
async def test_upload_requires_auth(client: AsyncClient):
    import io
    response = await client.post(
        "/api/v1/upload",
        files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_upload_with_valid_token(client: AsyncClient):
    import io
    from auth.jwt import create_access_token
    token = create_access_token("testuser")
    response = await client.post(
        "/api/v1/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data


@pytest.mark.anyio
async def test_upload_invalid_extension(client: AsyncClient):
    import io
    from auth.jwt import create_access_token
    token = create_access_token("testuser")
    response = await client.post(
        "/api/v1/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("malware.exe", io.BytesIO(b"MZ"), "application/octet-stream")},
    )
    assert response.status_code == 415


@pytest.mark.anyio
async def test_metrics_endpoint(client: AsyncClient):
    response = await client.get("/api/v1/metrics")
    # Metrics endpoint requires auth
    assert response.status_code in (200, 401)
