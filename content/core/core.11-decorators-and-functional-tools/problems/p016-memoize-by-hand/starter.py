from functools import wraps


def memoize(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.cache = {}
    return wrapper
