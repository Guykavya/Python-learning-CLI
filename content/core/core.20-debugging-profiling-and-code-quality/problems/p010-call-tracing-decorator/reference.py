import functools
import logging


def trace_calls(logger):
    """Decorator factory: log each call, its result or its exception at DEBUG."""

    def decorator(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not logger.isEnabledFor(logging.DEBUG):
                return func(*args, **kwargs)
            parts = [repr(a) for a in args]
            parts += [f"{key}={value!r}" for key, value in kwargs.items()]
            logger.debug("call %s(%s)", name, ", ".join(parts))
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                logger.debug("%s raised %r", name, exc)
                raise
            logger.debug("%s -> %r", name, result)
            return result

        return wrapper

    return decorator
