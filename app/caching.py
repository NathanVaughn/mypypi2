import functools
import time
from typing import Any, Callable

from loguru import logger

import app.data.sql


def repository_cache(func: Callable) -> Callable:
    """
    Caches the result of a function for a timeout specified by the function itself.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function.
    """

    cache = {}
    cache_times = {}

    @functools.wraps(func)
    def wrapper(*args: str, **kwargs: str) -> Any:
        # Get the timeout value from the function
        repository_slug = kwargs["repository_slug"]
        repository_timeout = app.data.sql.lookup_repository_timeout(repository_slug)

        key = (func.__name__, *args, *kwargs.items())

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
