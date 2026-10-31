from functools import wraps


def memoize(key=None):
    def decorator(func):
        cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            if key is None:
                k = (args, tuple(sorted(kwargs.items())))
            else:
                k = key(*args, **kwargs)
            if k in cache:
                return cache[k]
            result = func(*args, **kwargs)
            cache[k] = result
            return result

        def cache_clear():
            cache.clear()

        wrapper.cache = cache
        wrapper.cache_clear = cache_clear
        return wrapper
    return decorator
