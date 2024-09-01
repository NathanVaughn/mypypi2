import pathlib
import pickle
from typing import Any

from app.data.cache.base import BaseCache


class FileSystemCache(BaseCache):
    def __init__(self, directory: str) -> None:
        self._local_dir = pathlib.Path(directory)
        self._local_dir.mkdir(parents=True, exist_ok=True)

    def _set(self, key: str, value: Any) -> None:
        """
        Set a cache value
        """
        with open(self._local_dir.joinpath(key), "wb") as fp:
            pickle.dump(value, fp)

    def _get(self, key: str) -> Any | None:
        """
        Get a cache value. Returnm None if the key does not exist
        """
        try:
            with open(self._local_dir.joinpath(key), "rb") as fp:
                return pickle.load(fp)
        except FileNotFoundError:
            return None

    def _delete(self, key: str) -> None:
        """
        Delete a cache key
        """
        self._local_dir.joinpath(key).unlink(missing_ok=True)
