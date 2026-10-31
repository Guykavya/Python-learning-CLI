from functools import wraps


def deprecated(message, log=None):
    def decorator(func):
        return func
    return decorator
