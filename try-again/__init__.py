import time
import functools
from typing import Callable, Any, Tuple, Type, Optional


def retry(
    tries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    fallback: Optional[Callable[..., Any]] = None,
):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            
            for attempt in range(1, tries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == tries:
                        if fallback is not None:
                            return fallback(*args, **kwargs)
                        raise e
                    
                    time.sleep(current_delay)
                    current_delay *= backoff

        return wrapper
    return decorator
