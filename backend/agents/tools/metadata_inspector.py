from __future__ import annotations

from typing import Any
from uuid import UUID

from storage.qdrant_client import get_qdrant_client
from config import get_settings

settings = get_settings()


async def run_metadata_inspector(document_id: UUID | None = None) -> list[dict[str, Any]]:
    """
    LangGraph tool node: scroll through Qdrant payload metadata
    for a document or across the whole collection.
    """
    client = get_qdrant_client()
    scroll_filter = None
    if document_id:
        from qdrant_client.models import FieldCondition, Filter, MatchValue
        scroll_filter = Filter(
            must=[FieldCondition(key="document_id", match=MatchValue(value=str(document_id)))]
        )

    points, _ = await client.scroll(
        collection_name=settings.qdrant_collection,
        scroll_filter=scroll_filter,
        limit=50,
        with_payload=True,
        with_vectors=False,
    )
    return [{"id": str(p.id), "payload": p.payload} for p in points]
