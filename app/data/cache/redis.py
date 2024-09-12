from typing import Any

import redis

from app.data.cache.base import BaseCache


class RedisCache(BaseCache):
    def __init__(self, host: str, port: int, db: int) -> None:
        self._connection = redis.Redis(host=host, port=port, db=db)

    def _set(self, key: str, value: Any) -> None:
        """
        Set a cache value
        """
        self._connection.set(key, value)

    def _get(self, key: str) -> Any | None:
        """
        Get a cache value. Returnm None if the key does not exist
        """
        self._connection.get(key)

    def _delete(self, key: str) -> None:
        """
        Delete a cache key
        """
        self._connection.delete(key)
