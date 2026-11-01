## Approach

- **Hashable?** Asking forgiveness is the only complete test: `hash()` recurses into tuples and
  calls custom `__hash__` methods, and a class with `__hash__ = None` raises `TypeError`.
- **`Point`** hashes the same tuple that `__eq__` compares, so promise 1 holds. Making it
  immutable protects promise 2: if `x` cannot change, the hash cannot change.
- **Lost keys** come from the difference between iteration (walks the stored entries, no hashing)
  and lookup (hashes the key *now* and probes from that slot).
- **Collisions**: group by hash, but inside a group keep only pairwise non-equal values, because
  equal values sharing a hash is exactly what the first promise requires.

## Code

```python
def check_hashable(obj):
    try:
        hash(obj)
    except TypeError:
        return False
    return True


class Point:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "y", y)

    def __setattr__(self, name, value):
        raise AttributeError(f"Point is immutable; cannot set {name!r}")

    def __delattr__(self, name):
        raise AttributeError(f"Point is immutable; cannot delete {name!r}")

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"Point({self.x!r}, {self.y!r})"


def lost_keys(d):
    return [key for key in d if key not in d]


def hash_collisions(values):
    groups = {}
    for value in values:
        group = groups.setdefault(hash(value), [])
        if not any(value == seen for seen in group):
            group.append(value)
    return [group for group in groups.values() if len(group) >= 2]
```

Why exactly is `t` lost in the example? With hash 2 it was stored via slot `2 & 7 = 2`. After
the change its hash is 3, so the lookup starts at slot 3, finds an empty slot and stops. The entry
is still there (iteration sees it, and it still takes memory), but no lookup reaches it, and
`d[Tag("abc")] = ...` would even add a second entry that is equal to the first.

## Complexity

`check_hashable` costs whatever `hash()` costs (O(size) for a tuple). `lost_keys` is O(n) on
average. `hash_collisions` is O(n · g) where g is the largest group size (usually 1 or 2).

## Another way

A frozen dataclass gives `__eq__`, `__hash__` and immutability in a few lines. Its generated
repr is `Point(x=1, y=2)`, so this task still needs its own `__repr__`:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def __repr__(self):
        return f"Point({self.x!r}, {self.y!r})"
```

Assigning raises `dataclasses.FrozenInstanceError`, a subclass of `AttributeError`.
`typing.NamedTuple` works too, but then `Point(1, 2) == (1, 2)` is `True`, because it *is* a tuple.
