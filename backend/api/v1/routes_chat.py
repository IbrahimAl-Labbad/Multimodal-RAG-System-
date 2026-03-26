from __future__ import annotations

import hashlib
import json
import logging
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from agents.graph import rag_graph
from schemas.query import QueryRequest, QueryType
from pipelines.retrieval import classify_query
from storage.redis_client import cache_get, cache_set
from storage.qdrant_client import get_collection_version_hash

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat(request: Request, body: QueryRequest) -> StreamingResponse:
    """Stream a RAG response via SSE. Returns JSON event stream."""
    # ── Corpus-aware cache key ─────────────────────────────────────────────────
    # Include collection version hash so cache is invalidated after re-indexing
    corpus_hash = await get_collection_version_hash()
    doc_scope = ":".join(sorted(str(d) for d in body.document_ids)) if body.document_ids else "all"
    cache_key = hashlib.sha256(
        f"{body.query}:{body.query_type}:{doc_scope}:{corpus_hash}".encode()
    ).hexdigest()

    cached = await cache_get(cache_key)
    if cached:
        async def cached_stream():
            yield f"data: {json.dumps({'type': 'cached', 'answer': cached['answer'], 'citations': cached['citations']})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(cached_stream(), media_type="text/event-stream")

    # ── Classify query type ────────────────────────────────────────────────────
    query_type = body.query_type or classify_query(body.query)

    # ── Run LangGraph agent ────────────────────────────────────────────────────
    initial_state = {
        "query": body.query,
        "session_id": str(body.session_id),
        "query_type": query_type,
        "sub_queries": [],
        "retrieved_chunks": [],
        "reranked_chunks": [],
        "context": "",
        "answer": "",
        "verified": False,
        "citations": [],
        "document_ids": [str(d) for d in body.document_ids] if body.document_ids else None,
        "top_k": body.top_k,
    }

    # ── Stream with error handling ─────────────────────────────────────────────
    async def event_stream():
        try:
            final_state = await rag_graph.ainvoke(initial_state)
            answer = final_state["answer"]
            citations = final_state["citations"]

            # Cache the result (only on success)
            await cache_set(cache_key, {"answer": answer, "citations": citations}, ttl=300)

            yield f"data: {json.dumps({'type': 'session', 'session_id': str(body.session_id)})}\n\n"
            # Stream answer word by word for UX
            words = answer.split(" ")
            for word in words:
                yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"
            yield f"data: {json.dumps({'type': 'citations', 'citations': citations})}\n\n"
        except Exception as exc:
            logger.exception("Error during RAG graph execution")
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"
        finally:
            # Always close the stream cleanly
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
