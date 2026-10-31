import functools
from collections.abc import Callable
from typing import Generic, ParamSpec, TypedDict, TypeVar

K = TypeVar("K")
V = TypeVar("V")
P = ParamSpec("P")
R = TypeVar("R")

_MISSING = object()


class CacheStats(TypedDict):
    hits: int
    misses: int
    evictions: int
    size: int
    capacity: int


class LRUCache(Generic[K, V]):
    """A least-recently-used cache. The most recently used entry is the LAST one in the dict."""

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
