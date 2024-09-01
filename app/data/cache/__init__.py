from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask


class _ActiveCache:
    def init_app(self, flask_app: Flask) -> None:
        with flask_app.app_context():
            if flask_app.config["cache"]["driver"] == "memory":
                import app.data.cache.memory

                self.provider = app.data.cache.memory.MemoryCache()
            elif flask_app.config["cache"]["driver"] == "filesystem":
                import app.data.cache.filesystem

                self.provider = app.data.cache.filesystem.FileSystemCache(flask_app.config["cache"]["directory"])
            else:
                raise ValueError("Unknown storage driver")


ActiveCache = _ActiveCache()
