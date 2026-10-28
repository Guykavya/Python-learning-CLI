## Approach

Keep the entries in an `OrderedDict` and treat its order as "age": the start is the least
recently used key, the end is the most recently used one.

- **get**: on a miss, return the default and touch nothing. On a hit, `move_to_end(key)` and
  return the value.
- **put**: assign the value, then `move_to_end(key)`. The second step matters when the key
  already existed: assignment keeps an existing key where it was. If the dict is now bigger than
  the capacity, `popitem(last=False)` removes the oldest entry.

Check for a miss with `key in self._data`, not with the value, because `0` and `None` are valid
cached values.

## Code

```python
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError(f"capacity must be at least 1, got {capacity}")
        self._capacity = capacity
        self._data: OrderedDict = OrderedDict()

    def get(self, key, default=None):
        if key not in self._data:
            return default
        self._data.move_to_end(key)
        return self._data[key]

    def put(self, key, value) -> None:
        self._data[key] = value
        self._data.move_to_end(key)
        if len(self._data) > self._capacity:
            self._data.popitem(last=False)

    def __len__(self) -> int:
        return len(self._data)

    def keys(self) -> list:
        return list(self._data)
```

## Complexity

`get` and `put` are O(1). `keys()` is O(n). Memory O(capacity).

## Another way

Since Python 3.7 a plain dict keeps insertion order, so you can fake `move_to_end` with
`value = d.pop(key); d[key] = value`, and evict the oldest with `del d[next(iter(d))]`. It works,
but `OrderedDict` says what you mean and has `popitem(last=False)` built in. For caching function
results you would normally just use `functools.lru_cache` (core.11); this class is what it does
inside.
