from typing import Any

from pymemcache import serde
from pymemcache.client.base import Client

from app.data.cache.base import BaseCache


class MemcachedCache(BaseCache):
    def __init__(self, host: str, port: int) -> None:
        self._connection = Client(server=(host, port), serde=serde.pickle_serde)

    @property
    def _supports_ttl(self) -> bool:
        return True

    def _set(self, key: str, value: Any, ttl: int) -> None:
        """
        Set a cache value
        """
        self._connection.set(key, value, expire=ttl)

    def _get(self, key: str) -> Any | None:
        """
        Get a cache value. Returnm None if the key does not exist
        """
        return self._connection.get(key)

    def _delete(self, key: str) -> None:
        """
        Delete a cache key
        """
        self._connection.delete(key)
