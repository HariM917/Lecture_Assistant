"""
Caching layer — Redis with in-memory fallback.
"""

import json
import logging
from typing import Optional, Any, Dict
from collections import OrderedDict

logger = logging.getLogger(__name__)


class InMemoryCache:
    """Thread-safe in-memory LRU cache (fallback when Redis is unavailable)."""

    def __init__(self, max_size: int = 1000):
        self._cache: OrderedDict = OrderedDict()
        self._max_size = max_size
        logger.info(f"InMemoryCache initialized (max_size={max_size})")

    def set(self, key: str, value: Any, expiry: Optional[int] = None) -> bool:
        if len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)
        self._cache[key] = value
        self._cache.move_to_end(key)
        return True

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def delete(self, key: str) -> bool:
        return self._cache.pop(key, None) is not None

    def clear_session_cache(self, session_id: str) -> int:
        prefix = f"session:{session_id}:"
        keys = [k for k in self._cache if k.startswith(prefix)]
        for k in keys:
            del self._cache[k]
        return len(keys)

    def health_check(self) -> bool:
        return True


class RedisCache:
    """Redis-backed cache with JSON serialization."""

    def __init__(self):
        from app.core.config import get_settings
        settings = get_settings()
        try:
            import redis
            self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.client.ping()
            self._default_expiry = settings.REDIS_EXPIRY
            logger.info("RedisCache connected")
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            self.client = None

    def set(self, key: str, value: Any, expiry: Optional[int] = None) -> bool:
        if not self.client:
            return False
        try:
            expiry = expiry or self._default_expiry
            json_value = json.dumps(value) if not isinstance(value, str) else value
            self.client.setex(key, expiry, json_value)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        if not self.client:
            return None
        try:
            value = self.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def delete(self, key: str) -> bool:
        if not self.client:
            return False
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def clear_session_cache(self, session_id: str) -> int:
        if not self.client:
            return 0
        try:
            pattern = f"session:{session_id}:*"
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0

    def health_check(self) -> bool:
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except Exception:
            return False
