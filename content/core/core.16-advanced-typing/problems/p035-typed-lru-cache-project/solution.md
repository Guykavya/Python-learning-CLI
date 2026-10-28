## Approach

**Types first.** `LRUCache(Generic[K, V])` has a key type `K` and a value type `V`. Each method
mentions them where a key or value goes (`get(key: K) -> V | None`, `put(key: K, value: V)`).
`on_evict` is `Callable[[K, V], None] | None`: a function taking the evicted key and value.
`stats()` returns a `TypedDict` so callers get exact keys. `__contains__` takes `object`, because
`x in cache` may test any value, even of the wrong type, and just answers `False`. The decorator
uses a `ParamSpec`, so a memoized function keeps its signature.

**The data structure.** A plain `dict` remembers insertion order. We say the **last** key is the
most recently used. Using a key means removing and re-adding it (it moves to the end). The least
recently used key is the **first**: `next(iter(d))`. This gives O(1) `get`, `put` and eviction.
(`collections.OrderedDict.move_to_end` does the same job more directly.)

**The traps.** (1) `get` must not detect a miss with `value is None`, since `None` can be a real
value. (2) `peek` and `in` must not change recency or the counters, or looking would change the
answer. (3) Updating an existing key never evicts. (4) The callback runs after the new entry is in
and the old one is out. (5) The memoize key must ignore keyword order, and a `None` result must be
cached.

## Code

```python
import functools
from collections.abc import Callable
from typing import Generic, ParamSpec, TypedDict, TypeVar

K = TypeVar("K")
V = TypeVar("V")
P = ParamSpec("P")
R = TypeVar("R")


class CacheStats(TypedDict):
    hits: int
    misses: int
    evictions: int
    size: int
    capacity: int


class LRUCache(Generic[K, V]):
    def __init__(self, capacity: int, on_evict: Callable[[K, V], None] | None = None) -> None:
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self._capacity = capacity
        self._on_evict = on_evict
        self._data: dict[K, V] = {}
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    @property
    def capacity(self) -> int:
        return self._capacity

    def get(self, key: K) -> V | None:
        if key in self._data:
            self._hits += 1
            value = self._data.pop(key)
            self._data[key] = value
            return value
        self._misses += 1
        return None

    def __getitem__(self, key: K) -> V:
        if key in self._data:
            self._hits += 1
            value = self._data.pop(key)
            self._data[key] = value
            return value
        self._misses += 1
        raise KeyError(key)

    def put(self, key: K, value: V) -> None:
        if key in self._data:
            del self._data[key]
        self._data[key] = value
        if len(self._data) > self._capacity:
            oldest = next(iter(self._data))
            old_value = self._data.pop(oldest)
            self._evictions += 1
            if self._on_evict is not None:
                self._on_evict(oldest, old_value)

    def pop(self, key: K) -> V:
        return self._data.pop(key)

    def peek(self, key: K) -> V | None:
        return self._data.get(key)

    def keys(self) -> list[K]:
        return list(reversed(self._data))

    def items(self) -> list[tuple[K, V]]:
        return list(reversed(self._data.items()))

    def clear(self) -> None:
        self._data.clear()

    def stats(self) -> CacheStats:
        return {
            "hits": self._hits,
            "misses": self._misses,
            "evictions": self._evictions,
            "size": len(self._data),
            "capacity": self._capacity,
        }

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key: object) -> bool:
        return key in self._data


def lru_memoize(capacity: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        cache: LRUCache[tuple[tuple[object, ...], tuple[tuple[str, object], ...]], R] = LRUCache(capacity)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = (args, tuple(sorted(kwargs.items())))
            if key in cache:
                return cache[key]
            result = func(*args, **kwargs)
            cache.put(key, result)
            return result

        return wrapper

    return decorator
```

This passes `python -m mypy --strict solution.py` (checked with mypy 2.4.0).

## Complexity

`get`, `put`, `pop`, `peek`, `in` and `len` are O(1) on average. `keys` and `items` are O(n).
`lru_memoize` adds an O(k log k) sort of the k keyword arguments per call.

## Another way

`collections.OrderedDict` with `move_to_end(key)` and `popitem(last=False)` states the intent more
directly. A doubly linked list plus a dict is the classic interview version (what `OrderedDict`
does inside). For the real thing, `functools.lru_cache` already exists in the standard library.
