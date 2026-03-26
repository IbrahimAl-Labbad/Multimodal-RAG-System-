from __future__ import annotations

import hashlib
from typing import Any
from uuid import UUID

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from config import get_settings

settings = get_settings()

_client: AsyncQdrantClient | None = None


def get_qdrant_client() -> AsyncQdrantClient:
    global _client
    if _client is None:
        _client = AsyncQdrantClient(
            host=settings.qdrant_host, port=settings.qdrant_port
        )
    return _client


async def ensure_collection(
    client: AsyncQdrantClient,
    collection: str,
    vector_size: int,
) -> None:
    """Create the Qdrant collection if it does not already exist."""
    existing = await client.get_collections()
    names = [c.name for c in existing.collections]
    if collection not in names:
        await client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )


async def upsert_points(
    collection: str,
    points: list[dict[str, Any]],
) -> None:
    client = get_qdrant_client()
    structs = [
        PointStruct(
            id=str(p["id"]),
            vector=p["vector"],
            payload=p["payload"],
        )
        for p in points
    ]
    await client.upsert(collection_name=collection, points=structs)


async def search_points(
    collection: str,
    query_vector: list[float],
    top_k: int = 5,
    metadata_filter: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    client = get_qdrant_client()

    flt: Filter | None = None
    if metadata_filter:
        conditions = [
            FieldCondition(key=k, match=MatchValue(value=v))
            for k, v in metadata_filter.items()
        ]
        flt = Filter(must=conditions)

    results = await client.search(
        collection_name=collection,
        query_vector=query_vector,
        limit=top_k,
        query_filter=flt,
        with_payload=True,
    )

    return [
        {
            "id": r.id,
            "score": r.score,
            "payload": r.payload,
        }
        for r in results
    ]


async def get_collection_version_hash() -> str:
    """
    Return a lightweight fingerprint of the current collection state.
    Changes whenever documents are upserted or deleted, invalidating
    any cache keys that include this hash.
    """
    client = get_qdrant_client()
    try:
        info = await client.get_collection(settings.qdrant_collection)
        # Combine point count + segment count for a cheap state fingerprint
        fingerprint = f"{info.points_count}:{info.segments_count}"
        return hashlib.sha256(fingerprint.encode()).hexdigest()[:12]
    except Exception:
        return "no-collection"
