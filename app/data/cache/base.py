from __future__ import annotations

import abc
import datetime
from typing import Any


class BaseCache(abc.ABC):
    EXPIRATION_SUFFIX = "_expiration"

    @abc.abstractmethod
    def _set(self, key: str, value: Any) -> None:
        """
        Set a cache value
        """
        ...

    @abc.abstractmethod
    def _get(self, key: str) -> Any | None:
        """
        Get a cache value. Returnm None if the key does not exist
        """
        ...

    @abc.abstractmethod
    def _delete(self, key: str) -> None:
        """
        Delete a cache key
        """
        ...

    def set(self, key: str, value: Any, ttl: int) -> None:
        """
        Set a cache value, with a TTL in seconds
        """
        expiration = datetime.datetime.now() + datetime.timedelta(seconds=ttl)
        self._set(f"{key}{self.EXPIRATION_SUFFIX}", expiration.isoformat())
        self._set(key, value)

    def get(self, key: str) -> Any | None:
        """
        Get a cache value, or None if it does not exist or is expired
        """
        expiration = self._get(f"{key}{self.EXPIRATION_SUFFIX}")
        if expiration is None:
            return None

        if datetime.datetime.fromisoformat(expiration) < datetime.datetime.now():
            self._delete(key)
            self._delete(f"{key}{self.EXPIRATION_SUFFIX}")
            return None

        return self._get(key)
