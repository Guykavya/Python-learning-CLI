import inspect
from functools import wraps


def log_arguments(log):
    def decorator(func):
        sig = inspect.signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            parts = [f"{name}={value!r}" for name, value in bound.arguments.items()]
            log.append(f"{func.__name__}({', '.join(parts)})")
            return func(*args, **kwargs)
        return wrapper
    return decorator
