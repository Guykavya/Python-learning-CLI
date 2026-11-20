# A TTL + LRU cache

Chapter section 2.4 (time to live and eviction) and 2.5 (an in-process TTL + LRU cache). Write a small bounded cache:

- every entry **expires** `ttl` seconds after it was stored (an entry whose expiry time is reached, `expires_at <= now`, counts as missing);
- when the cache holds more than `maxsize` entries, it drops the **least recently used** one. Both `set` and a successful `get` count as "using" a key;
- it counts **hits** and **misses**.

The clock is a parameter, `now`, a function with no arguments that returns seconds. Tests pass a fake clock and move it, so nothing sleeps.

## What to write

```python
class TTLCache:
    def __init__(self, maxsize=128, ttl=60.0, now=time.monotonic): ...
    def get(self, key, default=None): ...     # value, or default on a miss (missing or expired)
    def set(self, key, value, ttl=None): ...  # ttl=None means "use the cache's ttl"
    def delete(self, key): ...                # no error if the key is missing
    def __len__(self): ...                    # number of stored entries
    hits: int                                 # attributes, start at 0
    misses: int
    hit_ratio                                 # a property: hits / (hits + misses), 0.0 before any get
```

An expired entry found by `get` is **removed** (lazy expiry), so it no longer counts in `len()`.

## Example

```python
clock = [0.0]
cache = TTLCache(maxsize=3, ttl=10, now=lambda: clock[0])
for key in "abc":
    cache.set(key, key.upper())
cache.get("a")          # 'A'   (a is now the most recently used)
cache.set("d", "D")     # full: evicts b, the least recently used
cache.get("b")          # None  (a miss)
clock[0] = 10.0
cache.get("a")          # None  (stored at 0 with ttl 10: expired at exactly 10)
cache.hits, cache.misses        # (1, 2)
```

A good structure is `collections.OrderedDict` mapping key -> `(expires_at, value)`: `move_to_end(key)` marks a key as most recently used and `popitem(last=False)` removes the least recently used.
