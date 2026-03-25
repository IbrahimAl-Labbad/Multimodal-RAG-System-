from __future__ import annotations

import json
from typing import Any

import redis.asyncio as aioredis

from config import get_settings

settings = get_settings()

_redis: aioredis.Redis | None = None  # type: ignore[type-arg]


def get_redis() -> aioredis.Redis:  # type: ignore[type-arg]
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis


async def cache_get(key: str) -> Any | None:
    redis = get_redis()
    value = await redis.get(key)
    if value is None:
        return None
    return json.loads(value)


async def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    redis = get_redis()
    await redis.set(key, json.dumps(value), ex=ttl)


async def cache_delete(key: str) -> None:
    redis = get_redis()
    await redis.delete(key)
