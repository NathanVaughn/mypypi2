from __future__ import annotations


from app.config import Config


class _ActiveCache:
    def __init__(self) -> None:
        if Config.cache.driver == "memory":
            import app.data.cache.memory

            self.provider = app.data.cache.memory.MemoryCache()
        elif Config.cache.driver == "filesystem":
            import app.data.cache.filesystem

            assert Config.cache.filesystem is not None
            self.provider = app.data.cache.filesystem.FileSystemCache(Config.cache.filesystem.directory)


ActiveCache = _ActiveCache()
