from __future__ import annotations

from schemas.document import ChunkType
from models.embeddings import embed_text, embed_text_clip
from schemas.query import QueryType
from storage.qdrant_client import search_points
from config import get_settings

settings = get_settings()


def classify_query(query: str) -> QueryType:
    """Simple heuristic classifier — can be replaced with a model."""
    image_keywords = {
        "image", "photo", "picture", "diagram", "chart", "figure",
        "show", "visual", "graph", "screenshot", "illustration",
    }
    words = set(query.lower().split())
    has_image = bool(words & image_keywords)
    has_text = len(query.split()) > 3
    if has_image and has_text:
        return QueryType.MIXED
    if has_image:
        return QueryType.IMAGE
    return QueryType.TEXT


async def retrieve(
    query: str,
    query_type: QueryType = QueryType.TEXT,
    top_k: int = 5,
    document_ids: list[str] | None = None,
) -> list[dict]:
    """Embed query and perform ANN search in Qdrant with optional doc filter."""
    if query_type == QueryType.IMAGE:
        vector = embed_text_clip(query)
    else:
        vector = embed_text(query)

    metadata_filter: dict = {}
    # Note: multi-doc filter would use 'should' conditions in production
    # Here we simplify to single doc_id for clarity
    if document_ids and len(document_ids) == 1:
        metadata_filter["document_id"] = document_ids[0]

    results = await search_points(
        collection=settings.qdrant_collection,
        query_vector=vector,
        top_k=top_k * 2,  # over-fetch before reranking
        metadata_filter=metadata_filter or None,
    )
    return results
