## Approach

Convert the text into a tuple of ints once, then let Python compare tuples. The same tuple feeds equality, ordering and the hash, so they always agree.

## Code

```python
from functools import total_ordering


@total_ordering
class Version:
    def __init__(self, text):
        parts = text.split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise ValueError(f"not a version: {text!r}")
        self.major, self.minor, self.patch = (int(p) for p in parts)
        self._key = (self.major, self.minor, self.patch)

    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._key == other._key

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._key < other._key

    def __hash__(self):
        return hash(self._key)

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self):
        return f"Version({str(self)!r})"
```

## Complexity

O(len(text)) to parse, O(1) to compare.

## Another way

Return `NotImplemented` from `__lt__` and let `total_ordering` do the rest; or use `NamedTuple` (later modules) which gives ordering for free. Real-world versions also have pre-release tags (`1.0.0-beta`), which need extra rules.
