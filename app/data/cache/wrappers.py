import functools
from typing import Any, Callable, TypeVar

from loguru import logger

import app.data.sql
from app.data.cache.active import CacheDriver

_R = TypeVar("_R")


def _key_generator(func: Callable, **kwargs: Any) -> str:
    """
    Generate a cache key for the given function and arguments.
    """
    return "-".join((func.__qualname__, *(str(i) for (k, v) in kwargs.items() for i in (k, v))))


def get_or_set(key: str, func: Callable[..., _R], ttl: int | None) -> _R:
    """
    Get a key from the cache, or set it if it does not exist.
    """

    response = CacheDriver.get(key)
    if response is not None:
        logger.debug(f"Cache hit for {key}")
        return response

    logger.debug(f"Cache miss for {key}")
    # Call the original function again to get the result
    # and cache the result
    result = func()
    CacheDriver.set(key, result, ttl=ttl)

    return result


def cache_permamently_decorator(func: Callable) -> Callable:
    """
    Caches a function with an infinite timeout.
    """

    @functools.wraps(func)
    def wrapper(**kwargs: str) -> Any:
        key = _key_generator(func, **kwargs)
        return get_or_set(key, lambda: func(**kwargs), None)

    return wrapper


def cache_repository_timeout_function(func: Callable[..., _R], repository_slug: str, kwargs: dict[str, Any]) -> _R:
    """
    Caches a function based on the given repository slug.
    Expects the repository_slug to be passed as a keyword argument.
    """

    repository_timeout = app.data.sql.get_repository_timeout(repository_slug)
    key = _key_generator(func, **kwargs)
    return get_or_set(key, lambda: func(**kwargs), repository_timeout)


def cache_repository_timeout_decorator(func: Callable) -> Callable:
    """
    Caches a flask view function based on the repository timeout.
    Expects the repository_slug to be passed as a keyword argument.
    """

    @functools.wraps(func)
    def wrapper(*args: str, **kwargs: str) -> Any:
        repository_timeout = app.data.sql.get_repository_timeout(kwargs["repository_slug"])

        # flask always passes the view function's arguments as kwargs
        # the second part of this line flattens the kwargs into a list
        key = _key_generator(func, **kwargs)
        return get_or_set(key, lambda: func(**kwargs), repository_timeout)

    return wrapper
