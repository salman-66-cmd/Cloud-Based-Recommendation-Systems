import json
import time
import logging
from typing import Optional, Any
from app.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis_client = None
        self.redis_available = False
        self._memory_cache = {}  # {key: (value, expiry_timestamp)}
        self.hits = 0
        self.misses = 0
        self._connect_redis()

    def _connect_redis(self):
        try:
            import redis
            client = redis.from_url(settings.REDIS_URL, socket_timeout=1.0, socket_connect_timeout=1.0)
            client.ping()
            self.redis_client = client
            self.redis_available = True
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            self.redis_available = False
            self.redis_client = None
            logger.info(f"Redis unavailable ({e}). Using in-memory caching fallback.")

    def get_json(self, key: str) -> Optional[Any]:
        if self.redis_available and self.redis_client:
            try:
                data = self.redis_client.get(key)
                if data:
                    self.hits += 1
                    return json.loads(data.decode("utf-8") if isinstance(data, bytes) else data)
                self.misses += 1
                return None
            except Exception as e:
                logger.warning(f"Redis get failed ({e}), falling back to memory.")
                self.redis_available = False

        # In-memory fallback
        now = time.time()
        if key in self._memory_cache:
            value, expiry = self._memory_cache[key]
            if expiry > now:
                self.hits += 1
                return value
            else:
                del self._memory_cache[key]
        self.misses += 1
        return None

    def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if ttl is None:
            ttl = settings.CACHE_EXPIRATION_SECONDS
        
        serialized = json.dumps(value)
        if self.redis_available and self.redis_client:
            try:
                self.redis_client.setex(key, ttl, serialized)
                return True
            except Exception as e:
                logger.warning(f"Redis set failed ({e}), falling back to memory.")
                self.redis_available = False

        # In-memory fallback
        self._memory_cache[key] = (value, time.time() + ttl)
        # Clean up expired keys occasionally
        if len(self._memory_cache) > 1000:
            now = time.time()
            self._memory_cache = {k: v for k, v in self._memory_cache.items() if v[1] > now}
        return True

    def delete(self, key: str) -> bool:
        if self.redis_available and self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception:
                pass
        self._memory_cache.pop(key, None)
        return True

    def delete_pattern(self, pattern: str) -> int:
        count = 0
        if self.redis_available and self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    count = self.redis_client.delete(*keys)
            except Exception:
                pass
        # Memory cache pattern match (simple prefix matching)
        prefix = pattern.replace("*", "")
        to_del = [k for k in self._memory_cache if prefix in k]
        for k in to_del:
            del self._memory_cache[k]
            count += 1
        return count

    def invalidate_user_cache(self, user_id: int):
        self.delete(f"recommendations:user:{user_id}")
        self.delete(f"recommendations:user:{user_id}:content")
        self.delete(f"recommendations:user:{user_id}:collab")
        self.delete(f"recommendations:user:{user_id}:hybrid")

    def get_stats(self) -> dict:
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0.0
        return {
            "backend": "redis" if self.redis_available else "memory",
            "redis_connected": self.redis_available,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_pct": round(hit_rate, 2),
            "memory_keys_count": len(self._memory_cache)
        }

cache = CacheService()
