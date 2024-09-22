from __future__ import annotations

from app.config import CacheDrivers, Config

if Config.cache.driver == CacheDrivers.MEMORY:
    import app.data.cache.memory

    CacheDriver = app.data.cache.memory.MemoryCache()

elif Config.cache.driver == CacheDrivers.FILESYSTEM:
    import app.data.cache.filesystem

    assert Config.cache.filesystem is not None
    CacheDriver = app.data.cache.filesystem.FileSystemCache(Config.cache.filesystem.directory)

elif Config.cache.driver == CacheDrivers.REDIS:
    import app.data.cache.redis

    assert Config.cache.redis is not None
    CacheDriver = app.data.cache.redis.RedisCache(
        host=Config.cache.redis.host, port=Config.cache.redis.port, db=Config.cache.redis.db
    )

elif Config.cache.driver == CacheDrivers.MEMCACHED:
    import app.data.cache.memcached

    assert Config.cache.memcached is not None
    CacheDriver = app.data.cache.memcached.MemcachedCache(
        host=Config.cache.memcached.host, port=Config.cache.memcached.port
    )

elif Config.cache.driver == CacheDrivers.DATABASE:
    import app.data.cache.database

    CacheDriver = app.data.cache.database.DatabaseCache()
