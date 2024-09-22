from __future__ import annotations

import abc
import datetime
from typing import Any

NEVER = "NEVER"


class BaseCache(abc.ABC):
    EXPIRATION_SUFFIX = "_expiration"

    @property
    @abc.abstractmethod
    def _supports_ttl(self) -> bool:
        """
        Return whether or not the cache implementation supports TTL.
        If not, the TTL will be stored as a seperate cache key.
        """
        ...

    @abc.abstractmethod
    def _set(self, key: str, value: Any, ttl: int | None = None) -> None:
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

    def set(self, key: str, value: Any, ttl: int | None) -> None:
        """
        Set a cache value, with a TTL in seconds
        """
        self._set(key, value, ttl=ttl)

        if not self._supports_ttl:
            if ttl is not None:
                expiration = datetime.datetime.now() + datetime.timedelta(seconds=ttl)
                expiration_value = expiration.isoformat()
            else:
                expiration_value = NEVER

            self._set(f"{key}{self.EXPIRATION_SUFFIX}", expiration_value)

    def get(self, key: str) -> Any | None:
        """
        Get a cache value, or None if it does not exist or is expired
        """
        if not self._supports_ttl:
            expiration = self._get(f"{key}{self.EXPIRATION_SUFFIX}")

            if expiration == NEVER:
                # skip to end
                pass

            elif expiration is None:
                # somehow expiration key is lost
                return None

            elif datetime.datetime.fromisoformat(expiration) < datetime.datetime.now():
                self._delete(key)
                self._delete(f"{key}{self.EXPIRATION_SUFFIX}")
                return None

        return self._get(key)
