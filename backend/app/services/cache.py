import redis
import json
import logging
from typing import Optional, Any, Dict
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RedisCache:
    """Manages Redis caching for sessions and processed data."""
    
    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.redis_client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Redis not available (mock mode): {e}")
            self.redis_client = None
    
    def set(self, key: str, value: Any, expiry: Optional[int] = None) -> bool:
        """Set value in cache."""
        if not self.redis_client:
            return False
        
        try:
            expiry = expiry or settings.REDIS_EXPIRY
            json_value = json.dumps(value) if not isinstance(value, str) else value
            self.redis_client.setex(key, expiry, json_value)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear_session_cache(self, session_id: str) -> int:
        """Clear all cache data for a session."""
        if not self.redis_client:
            return 0
        
        try:
            pattern = f"session:{session_id}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0
    
    def health_check(self) -> bool:
        """Check Redis connection health."""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            return False


redis_cache = RedisCache()
