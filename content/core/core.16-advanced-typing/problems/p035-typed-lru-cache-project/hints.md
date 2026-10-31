## Hint 1

Do the structure first, with all hints, and the behaviour second. Which two `TypeVar`s does `LRUCache` need, and where does each appear in the method signatures? Then think about the data structure: a dict keeps insertion order. If the *last* key is the most recently used, what do `get` and `put` do to the dict, and which key is the one to evict?

## Hint 2

"Use" a key = `value = self._data.pop(key); self._data[key] = value`. The oldest key is `next(iter(self._data))`. Test presence with `key in self._data`, never with `value is None` (the value may be `None`). Keep `_hits`, `_misses` and `_evictions` as private counters; `stats()` builds a `CacheStats` dict from them. `keys()` is `list(reversed(self._data))`.

For `lru_memoize`: build the key as `(args, tuple(sorted(kwargs.items())))`; check `key in cache` (does not touch the stats), then `cache[key]` (refreshes recency); otherwise call, `put`, return. The wrapper is `(*args: P.args, **kwargs: P.kwargs) -> R` with `functools.wraps`.

## Hint 3

```
K, V = TypeVar; P = ParamSpec; R = TypeVar
class CacheStats(TypedDict): hits, misses, evictions, size, capacity (all int)

class LRUCache(Generic[K, V]):
    __init__(capacity: int, on_evict: Callable[[K, V], None] | None = None) -> None:
        capacity < 1 -> ValueError ; self._data: dict[K, V] = {} ; counters = 0
    get: if key in data: hits += 1; move to end; return value   else misses += 1; return None
    put: remove key if present; data[key] = value
         if len(data) > capacity: oldest = next(iter(data)); old = data.pop(oldest); evictions += 1
                                   call on_evict(oldest, old) when it is not None
    keys: list(reversed(data))        items: list(reversed(data.items()))
    stats: {"hits": ..., "size": len(data), "capacity": ...}
```
