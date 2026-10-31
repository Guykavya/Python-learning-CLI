from functools import wraps


def memoize(key=None):
    def decorator(func):
        return func
    return decorator
