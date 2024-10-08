from app.data.cache.base import BaseCache


class MemoryCache(BaseCache):
    def __init__(self):
        self._cache = {}

    @property
    def _supports_ttl(self) -> bool:
        return False

    def _set(self, key: str, value: str, ttl: None = None) -> None:
        """
        Set a cache value
        """
        self._cache[key] = value

    def _get(self, key: str) -> str | None:
        """
        Get a cache value. Returnm None if the key does not exist
        """
        return self._cache.get(key, None)

    def _delete(self, key: str) -> None:
        """
        Delete a cache key
        """
        if key in self._cache:
            del self._cache[key]
