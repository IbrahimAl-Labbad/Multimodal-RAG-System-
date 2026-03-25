from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
from schemas.response import IndexResponse
from workers.tasks import ingest_document_task

router = APIRouter(tags=["index"])


class IndexRequest(BaseModel):
    document_id: UUID
    filename: str


@router.post("/index", response_model=IndexResponse)
async def index_document(request: Request, body: IndexRequest) -> dict:
    """Trigger the Celery ingestion + indexing pipeline for an uploaded file."""
    task = ingest_document_task.delay(str(body.document_id), body.filename)
    # Return accepted — the real result is async via Celery
    return {
        "document_id": str(body.document_id),
        "text_chunks": 0,
        "image_chunks": 0,
        "table_chunks": 0,
        "total_chunks": 0,
        "elapsed_seconds": 0.0,
        "task_id": task.id,
    }
