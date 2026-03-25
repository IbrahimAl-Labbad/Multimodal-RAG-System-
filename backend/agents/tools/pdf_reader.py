from __future__ import annotations

from typing import Any
from uuid import UUID

from pipelines.ingestion import ingest_pdf


async def run_pdf_reader(file_bytes: bytes, filename: str, document_id: UUID | None = None) -> dict[str, Any]:
    """LangGraph tool node: parse and chunk a PDF file on demand."""
    result = await ingest_pdf(file_bytes, filename, document_id)
    return result.model_dump(mode="json")
