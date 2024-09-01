import functools
import time
from typing import Any, Callable

from loguru import logger

import app.data.sql


def repository_cache(func: Callable) -> Callable:
    """
    Caches a flask view function based on the repository timeout.
    Expects the repository_slug to be passed as a keyword argument.
    """

    cache = {}
    cache_times = {}

    @functools.wraps(func)
    def wrapper(*args: str, **kwargs: str) -> Any:
        repository_timeout = app.data.sql.get_repository_timeout(kwargs["repository_slug"])

        # flask always passes the view function's arguments as kwargs
        # the second part of this line flattens the kwargs into a list
        key = "-".join((func.__name__, *args, *(i for (k, v) in kwargs.items() for i in (k, v))))

        if key in cache and time.time() - cache_times[key] < repository_timeout:
            logger.debug(f"Cache hit for {key}")
            return cache[key]

        # Call the original function again to get the result
        logger.debug(f"Cache miss for {key}")
        result = func(*args, **kwargs)
        cache[key] = result
        cache_times[key] = time.time()
        return result

    return wrapper
