import functools


class Memoize:
    def __init__(self, func):
        self.func = func
        self.cache = {}
        self.hits = 0
        self.misses = 0
        self.uncached = 0

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
