import pickle
from typing import Any

import redis

from app.data.cache.base import BaseCache


class RedisCache(BaseCache):
    def __init__(self, host: str, port: int, db: int) -> None:
        self._connection = redis.Redis(host=host, port=port, db=db)

    @property
    def _supports_ttl(self) -> bool:
        return True

    def _set(self, key: str, value: Any, ttl: int) -> None:
        """
        Set a cache value
        """
        self._connection.set(key, pickle.dumps(value), ex=ttl)

    def _get(self, key: str) -> Any | None:
        """
        Get a cache value. Returnm None if the key does not exist
        """
        value: Any | None = self._connection.get(key)
        if value is not None:
            return pickle.loads(value)

        return None

    def _delete(self, key: str) -> None:
        """
        Delete a cache key
        """
        self._connection.delete(key)
