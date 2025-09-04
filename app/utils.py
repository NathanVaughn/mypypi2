import functools
import time
from contextlib import contextmanager
from typing import Any, Callable, Generator

from flask import url_for
from loguru import logger

from app.config import Config


def url_for_scheme(
    endpoint: str,
    *,
    _external: bool | None = None,
    **values: Any,
) -> str:
    """
    Overwrite the default url_for to use the configured URL scheme
    Flask detects the scheme from the request context, but this can fail in
    reverse proxy setups.
    """
    # https://stackoverflow.com/a/62960919
    return url_for(endpoint=endpoint, _scheme=Config.base_url.scheme, _external=_external, **values)


@contextmanager
def time_this_context(message: str) -> Generator:
    """
    Time a block of code. Logs the time it took to execute the block.
    """
    start = time.time()
    yield
    logger.debug(f"{message} in {time.time() - start:.2f} seconds")


def time_this_decorator(message: str) -> Callable:
    """
    Time a block of code. Logs the time it took to execute the block.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: str, **kwargs: str) -> Any:
            start = time.time()
            result = func(*args, **kwargs)
            logger.debug(f"{message} in {time.time() - start:.2f} seconds")
            return result

        return wrapper

    return decorator
