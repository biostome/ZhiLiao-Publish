from __future__ import annotations

import hashlib
import json
from datetime import timedelta
from typing import Any

import redis
from ..config import settings


_redis_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


def compute_item_hash(*parts: Any) -> str:
    normalized = ":".join([json.dumps(p, sort_keys=True, ensure_ascii=False) if not isinstance(p, str) else p for p in parts])
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def is_duplicate(dedup_key: str, ttl_days: int | None = None) -> bool:
    try:
        client = get_redis()
        ttl_days = ttl_days or settings.DUP_TTL_DAYS
        key = f"dedupe:{dedup_key}"
        added = client.set(name=key, value="1", nx=True, ex=timedelta(days=ttl_days))
        return added is None
    except Exception:
        # If Redis is unavailable, do not treat as duplicate to avoid data loss
        return False