## Approach

The class is generic in two variables. The state is a `dict[K, V]`, and every method says in its signature how the key and value types flow: keys go **in** (`add`, `get`, `require`, `remove`, `__contains__`), values come **out** (`get`, `require`, `remove`, `find`, `all`). `get` is the only method whose result may be missing, so only it returns `V | None`; a caller must check for `None`, while `require` is the method for "I know it is there".

Python's dict keeps insertion order, so `find` and `all` need no extra bookkeeping. `get` uses `dict.get`, and `add` uses `key in self._data` (not `.get(key)`), so that a stored `None` or `0` is still seen as present.

## Code

```python
from collections.abc import Callable
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class Repository(Generic[K, V]):
    def __init__(self) -> None:
        self._data: dict[K, V] = {}

    def add(self, key: K, value: V) -> None:
        if key in self._data:
            raise KeyError(key)
        self._data[key] = value

    def get(self, key: K) -> V | None:
        return self._data.get(key)

    def require(self, key: K) -> V:
        return self._data[key]

    def remove(self, key: K) -> V:
        return self._data.pop(key)

    def find(self, predicate: Callable[[V], bool]) -> list[V]:
        return [v for v in self._data.values() if predicate(v)]

    def all(self) -> list[V]:
        return list(self._data.values())

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key: K) -> bool:
        return key in self._data
```

## Complexity

`add`, `get`, `require`, `remove`, `len`, `in`: O(1) on average. `find` and `all`: O(n).

## Another way

Python 3.12+: `class Repository[K, V]:`. To make the key type more specific, bound it: `K` bound to `Hashable`, because dict keys must be hashable (`class Repository[K: Hashable, V]`). In larger programs a `Repository[int, User]` is often given a subclass, `class UserRepo(Repository[int, User])`, which adds user-specific queries and keeps all the inherited, correctly-typed methods.
