from functools import lru_cache

from app.shared.cache import AppCache


@lru_cache
def get_cache() -> AppCache:
    return AppCache.from_settings()