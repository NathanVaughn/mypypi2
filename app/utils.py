import functools
import time
from contextlib import contextmanager
from typing import Any, Callable, Generator

from loguru import logger


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
