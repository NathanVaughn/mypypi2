import functools
from typing import Any, Callable

from loguru import logger

import app.data.sql
from app.data.cache.active import CacheDriver


def repository_cache(func: Callable) -> Callable:
    """
    Caches a flask view function based on the repository timeout.
    Expects the repository_slug to be passed as a keyword argument.
    """

    @functools.wraps(func)
    def wrapper(*args: str, **kwargs: str) -> Any:
        repository_timeout = app.data.sql.get_repository_timeout(kwargs["repository_slug"])

        # flask always passes the view function's arguments as kwargs
        # the second part of this line flattens the kwargs into a list
        key = "-".join((func.__qualname__, *args, *(i for (k, v) in kwargs.items() for i in (k, v))))

        response = CacheDriver.get(key)
        if response is not None:
            logger.debug(f"Cache hit for {key}")
            return response

        # Call the original function again to get the result
        # and cache the result
        logger.debug(f"Cache miss for {key}")
        result = func(*args, **kwargs)
        CacheDriver.set(key, result, repository_timeout)
        return result

    return wrapper
