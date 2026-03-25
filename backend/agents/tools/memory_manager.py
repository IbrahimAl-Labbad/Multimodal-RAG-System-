from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from storage.redis_client import get_redis

SESSION_TTL = 3600  # 1 hour


def _session_key(session_id: UUID) -> str:
    return f"session:{session_id}"


async def get_session_memory(session_id: UUID) -> list[dict[str, Any]]:
    """Retrieve conversation history from Redis for a session."""
    redis = get_redis()
    raw = await redis.get(_session_key(session_id))
    if raw is None:
        return []
    return json.loads(raw)  # type: ignore[return-value]


async def append_session_memory(
    session_id: UUID,
    role: str,
    content: str,
) -> None:
    """Append a message to the session memory in Redis."""
    redis = get_redis()
    history = await get_session_memory(session_id)
    history.append({"role": role, "content": content})
    await redis.set(_session_key(session_id), json.dumps(history), ex=SESSION_TTL)


async def clear_session_memory(session_id: UUID) -> None:
    redis = get_redis()
    await redis.delete(_session_key(session_id))
