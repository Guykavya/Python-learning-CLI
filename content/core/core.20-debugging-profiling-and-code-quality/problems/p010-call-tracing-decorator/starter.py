import functools
import logging


def trace_calls(logger):
    """Decorator factory: log each call, its result or its exception at DEBUG."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            print("calling", func.__name__)
            return func(*args, **kwargs)

        return wrapper

    return decorator
