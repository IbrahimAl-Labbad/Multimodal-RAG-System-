from __future__ import annotations

from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class QueryType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    MIXED = "mixed"


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4096)
    session_id: UUID = Field(default_factory=uuid4)
    document_ids: list[UUID] | None = None  # filter retrieval to specific docs
    top_k: int = Field(default=5, ge=1, le=20)
    query_type: QueryType = QueryType.TEXT
    history: list[ChatMessage] = Field(default_factory=list)
