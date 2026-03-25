from __future__ import annotations

from schemas.query import QueryType
from pipelines.retrieval import retrieve


async def run_vector_retriever(
    query: str,
    query_type: QueryType = QueryType.TEXT,
    top_k: int = 5,
    document_ids: list[str] | None = None,
) -> list[dict]:
    """LangGraph tool node: query Qdrant with ANN search + metadata filters."""
    return await retrieve(query, query_type, top_k, document_ids)
