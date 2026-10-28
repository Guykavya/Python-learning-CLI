## Approach

`in` is just a call to `__contains__`. For `Interval` that is a comparison (no storing, works for floats and huge ranges). For `WordSet` it is a set lookup on normalised words.

## Code

```python
class Interval:
    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi

    def __contains__(self, item):
        if not isinstance(item, (int, float)):
            return False
        return self.lo <= item <= self.hi


class WordSet:
    def __init__(self, words):
        self._words = {w.casefold() for w in words}

    def __contains__(self, item):
        if not isinstance(item, str):
            return False
        return item.casefold() in self._words
```

## Complexity

`Interval`: O(1). `WordSet`: O(1) average per lookup, O(n) to build.

## Another way

Implement `__iter__` instead and let `in` scan: it works but is O(n) and impossible for an interval of floats.
