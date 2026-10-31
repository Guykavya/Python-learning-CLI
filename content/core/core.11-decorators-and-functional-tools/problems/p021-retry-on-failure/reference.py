import time
from functools import wraps


def retry(attempts, exceptions=(Exception,), delay=0.0, sleep=time.sleep):
    if attempts < 1:
        raise ValueError(f"attempts must be at least 1, got {attempts}")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == attempts:
                        raise
                    sleep(delay)
        return wrapper
    return decorator
