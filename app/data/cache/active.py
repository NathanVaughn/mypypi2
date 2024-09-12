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

        elif Config.cache.driver == "redis":
            import app.data.cache.redis

            assert Config.cache.redis is not None
            self.provider = app.data.cache.redis.RedisCache(
                host=Config.cache.redis.host, port=Config.cache.redis.port, db=Config.cache.redis.db
            )


ActiveCache = _ActiveCache()
