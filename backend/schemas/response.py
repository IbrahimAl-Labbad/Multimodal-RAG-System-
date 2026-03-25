from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: UUID
    document_id: UUID
    filename: str
    page_number: int | None = None
    chunk_type: str
    excerpt: str
    relevance_score: float = Field(ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    session_id: UUID
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    query_type: str = "text"
    latency_ms: float = 0.0


class UploadResponse(BaseModel):
    document_id: UUID
    filename: str
    size_bytes: int
    message: str = "File uploaded successfully"


class IndexResponse(BaseModel):
    document_id: UUID
    text_chunks: int
    image_chunks: int
    table_chunks: int
    total_chunks: int
    elapsed_seconds: float


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
