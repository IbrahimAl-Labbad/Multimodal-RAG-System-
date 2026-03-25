from __future__ import annotations

import json
from collections.abc import AsyncIterator
from uuid import UUID

from models.llm import generate_stream
from schemas.response import Citation
from config import get_settings

settings = get_settings()


def _build_context(chunks: list[dict]) -> str:
    """Assemble retrieved chunks into a structured context string."""
    parts: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        payload = chunk.get("payload", {})
        content = payload.get("content", payload.get("caption", ""))
        chunk_type = payload.get("chunk_type", "text")
        filename = payload.get("filename", "unknown")
        page = payload.get("page_number", "?")
        parts.append(f"[Source {i} | {chunk_type} | {filename} p.{page}]\n{content}")
    return "\n\n---\n\n".join(parts)


def _build_citations(chunks: list[dict]) -> list[Citation]:
    return [
        Citation(
            chunk_id=UUID(str(c.get("id", "00000000-0000-0000-0000-000000000000"))),
            document_id=UUID(str(c["payload"].get("document_id", "00000000-0000-0000-0000-000000000000"))),
            filename=c["payload"].get("filename", ""),
            page_number=c["payload"].get("page_number"),
            chunk_type=c["payload"].get("chunk_type", "text"),
            excerpt=c["payload"].get("content", "")[:200],
            relevance_score=round(c.get("score", 0.0), 4),
        )
        for c in chunks
    ]


async def generate_streaming_response(
    query: str,
    chunks: list[dict],
    session_id: UUID,
) -> AsyncIterator[str]:
    """Yield SSE-formatted tokens and a final citations event."""
    context = _build_context(chunks)

    # Optional chain-of-thought prefix (hidden, configurable via env)
    prompt = query
    if settings.enable_chain_of_thought:
        prompt = (
            f"Think step by step before answering.\n"
            f"Question: {query}"
        )

    yield f"data: {json.dumps({'type': 'session', 'session_id': str(session_id)})}\n\n"

    async for token in generate_stream(prompt, context):
        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

    citations = _build_citations(chunks)
    citations_data = [c.model_dump(mode="json") for c in citations]
    yield f"data: {json.dumps({'type': 'citations', 'citations': citations_data})}\n\n"
    yield "data: [DONE]\n\n"
