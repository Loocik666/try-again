import time
import asyncio
import functools
import inspect
import logging
import random
from typing import Callable, Any, Tuple, Type, Optional, Union

ExceptionTypes = Tuple[Type[BaseException], ...]

def _check_exceptions_tuple(excs: ExceptionTypes) -> None:
    if not isinstance(excs, tuple) or not excs:
        raise TypeError("exceptions must be a non-empty tuple of exception types")
    for e in excs:
        if not isinstance(e, type) or not issubclass(e, BaseException):
            raise TypeError("each item in exceptions must be an exception class")

def retry(
    tries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: ExceptionTypes = (Exception,),
    fallback: Optional[Callable[..., Any]] = None,
    jitter: float = 0.0,
    max_delay: Optional[float] = None,
    logger: Optional[logging.Logger] = None,
):
    if not isinstance(tries, int) or tries < 1:
        raise ValueError("tries must be integer >= 1")
    if delay < 0:
        raise ValueError("delay must be >= 0")
    if backoff <= 0:
        raise ValueError("backoff must be > 0")
    if not (0.0 <= jitter <= 1.0):
        raise ValueError("jitter must be between 0.0 and 1.0")

    _check_exceptions_tuple(exceptions)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        is_coro = inspect.iscoroutinefunction(func)

        if logger is None:
            _logger = logging.getLogger(func.__module__)
        else:
            _logger = logger

        if is_coro:
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                current_delay = delay
                for attempt in range(1, tries + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions:
                        _logger.debug("Attempt %d/%d failed for %s", attempt, tries, func.__name__)
                        if attempt == tries:
                            if fallback is not None:
                                return fallback(*args, **kwargs)
                            raise
                        sleep_time = current_delay
                        if jitter:
                            mult = 1 + random.uniform(-jitter, jitter)
                            sleep_time *= mult
                        if max_delay is not None:
                            sleep_time = min(sleep_time, max_delay)
                        await asyncio.sleep(sleep_time)
                        current_delay = current_delay * backoff
            return async_wrapper

        else:
            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                current_delay = delay
                for attempt in range(1, tries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions:
                        _logger.debug("Attempt %d/%d failed for %s", attempt, tries, func.__name__)
                        if attempt == tries:
                            if fallback is not None:
                                return fallback(*args, **kwargs)
                            raise
                        sleep_time = current_delay
                        if jitter:
                            mult = 1 + random.uniform(-jitter, jitter)
                            sleep_time *= mult
                        if max_delay is not None:
                            sleep_time = min(sleep_time, max_delay)
                        time.sleep(sleep_time)
                        current_delay = current_delay * backoff
            return sync_wrapper

    return decorator
