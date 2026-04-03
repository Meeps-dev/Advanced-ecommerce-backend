import json
import logging
from typing import Any

from redis import Redis

from app.core.config import settings


logger = logging.getLogger(__name__)


class AppCache:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

   # --- FACTORY METHOD ---
    @classmethod
    def from_settings(cls) -> "AppCache":
        client = Redis.from_url(settings.redis_url, decode_responses=True)
        return cls(redis_client=client)
    
    # --- CORE CACHE METHODS ---
    def get_json(self, key: str) -> Any | None:
        try:
            raw = self.redis.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception:
            logger.warning("cache_get_failed", extra={"event": "cache_get_failed", "key": key}, exc_info=True)
            return None

    def set_json(self, key: str, value: Any, ttl_seconds: int) -> None:
        try:
            self.redis.setex(key, ttl_seconds, json.dumps(value))
        except Exception:
            logger.warning("cache_set_failed", extra={"event": "cache_set_failed", "key": key}, exc_info=True)

    def delete(self, *keys: str) -> None:
        valid_keys = [key for key in keys if key]
        if not valid_keys:
            return
        try:
            self.redis.delete(*valid_keys)
        except Exception:
            logger.warning("cache_delete_failed", extra={"event": "cache_delete_failed"}, exc_info=True)

    def delete_pattern(self, pattern: str) -> None:
        try:
            cursor = 0
            while True:
                cursor, keys = self.redis.scan(cursor=cursor, match=pattern, count=100)
                if keys:
                    self.redis.delete(*keys)
                if cursor == 0:
                    break
        except Exception:
            logger.warning(
                "cache_delete_pattern_failed",
                extra={"event": "cache_delete_pattern_failed", "pattern": pattern},
                exc_info=True,
            )