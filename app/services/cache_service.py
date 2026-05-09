from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class CacheService:
    """
    Simple in-memory TTL cache
    """

    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None

        if time.time() >= entry.expires_at:
            self._store.pop(key, None)
            return None

        return entry.value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = CacheEntry(
            value=value,
            expires_at=time.time() + self.ttl_seconds,
        )

    def invalidate_all(self) -> None:
        self._store.clear()

    def size(self) -> int:
        return len(self._store)
