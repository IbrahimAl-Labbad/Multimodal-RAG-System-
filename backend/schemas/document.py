from __future__ import annotations

from enum import Enum
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ChunkType(str, Enum):
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    OCR = "ocr"


class DocumentMetadata(BaseModel):
    document_id: UUID = Field(default_factory=uuid4)
    filename: str
    page_number: int | None = None
    section: str | None = None
    chunk_type: ChunkType = ChunkType.TEXT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    extra: dict[str, Any] = Field(default_factory=dict)


class TextChunk(BaseModel):
    chunk_id: UUID = Field(default_factory=uuid4)
    content: str
    embedding: list[float] | None = None
    metadata: DocumentMetadata


class ImageChunk(BaseModel):
    chunk_id: UUID = Field(default_factory=uuid4)
    image_bytes: bytes | None = None
    image_path: str | None = None
    caption: str | None = None
    embedding: list[float] | None = None
    metadata: DocumentMetadata


class TableChunk(BaseModel):
    chunk_id: UUID = Field(default_factory=uuid4)
    content: str  # Markdown / HTML representation
    embedding: list[float] | None = None
    metadata: DocumentMetadata


class IngestionResult(BaseModel):
    document_id: UUID
    filename: str
    text_chunks: int = 0
    image_chunks: int = 0
    table_chunks: int = 0
    total_chunks: int = 0
    elapsed_seconds: float = 0.0
