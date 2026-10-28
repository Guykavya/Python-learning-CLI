## Approach

A `Memoize` object is a function-like cache: the arguments are the question, the result is the answer. A dict is the natural store, and the only real work is the **key**. `args` is already a tuple (hashable if its items are). `kwargs` becomes `tuple(sorted(kwargs.items()))` so that the same set of keywords always gives the same key. Hashing happens when the key is looked up in the dict; if an argument is unhashable, that lookup raises `TypeError` and we fall back to calling the function.

Recursion works because the decorator **replaces** the name `fib` by the `Memoize` object, so the `fib(n - 1)` inside the function calls the cached version.

## Code

```python
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
```

## Complexity

A hit is O(size of the key). The cache grows by one entry per distinct call: O(number of distinct calls) memory. `fib(n)` becomes O(n) instead of O(2^n).

## Another way

`functools.lru_cache(maxsize=None)` or `functools.cache` does this (and more, including a size limit) in the standard library. Writing it yourself shows what the decorator does.
