import datetime
import pickle
from typing import Any

import app.data.sql
from app.data.cache.base import BaseCache
from app.models.cache import Cache


class DatabaseCache(BaseCache):
    @property
    def _supports_ttl(self) -> bool:
        return True

    def _set(self, key: str, value: Any, ttl: int) -> None:
        """
        Set a cache value
        """
        cache = Cache(
            key=key, value=pickle.dumps(value), expiration=datetime.datetime.now() + datetime.timedelta(seconds=ttl)
        )
        app.data.sql.session_save(cache)

    def _get(self, key: str) -> Any | None:
        """
        Get a cache value. Returnm None if the key does not exist
        """
        cache = app.data.sql.get_cache(key)
        if cache is None:
            return None

        if cache.is_expired:
            self._delete(key)
            return None

        return pickle.loads(cache.value)

    def _delete(self, key: str) -> None:
        """
        Delete a cache key
        """
        cache = app.data.sql.get_cache(key)
        if cache is None:
            return

        app.data.sql.session_delete(cache)
