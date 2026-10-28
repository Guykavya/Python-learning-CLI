import functools


class Memoize:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.cache = {}
        self.hits = 0
        self.misses = 0
        self.uncached = 0

    def __call__(self, *args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        try:
            if key in self.cache:
                self.hits += 1
                return self.cache[key]
        except TypeError:                    # unhashable argument
            self.uncached += 1
            return self.func(*args, **kwargs)
        self.misses += 1
        result = self.func(*args, **kwargs)
        self.cache[key] = result
        return result

    def cache_clear(self):
        self.cache.clear()
        self.hits = self.misses = self.uncached = 0
