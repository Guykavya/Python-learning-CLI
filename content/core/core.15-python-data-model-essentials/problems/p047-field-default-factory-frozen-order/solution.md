## Approach

Each option is a switch for one generated method: `default_factory` runs inside the generated `__init__`; `repr=False`/`compare=False` remove a field from the generated `__repr__`/`__eq__`; `order=True` adds comparison methods that compare `(major, minor, patch)` tuples; `frozen=True` adds `__setattr__`/`__delattr__` that raise, and with `eq=True` also generates `__hash__` from the fields (see problem 054 for why that matters).

## Code

```python
from dataclasses import dataclass, field


@dataclass
class Playlist:
    name: str
    songs: list = field(default_factory=list)
    plays: int = field(default=0, repr=False, compare=False)


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int = 0
    patch: int = 0

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"
```

## Complexity

Generated comparisons are O(number of fields).

## Another way

`@dataclass(order=True)` without `frozen` is possible too, but then the objects are mutable and unhashable. `functools.total_ordering` and a hand-written `__lt__` give the same ordering with more code. A `typing.NamedTuple` is ordered by default (it is a tuple).
