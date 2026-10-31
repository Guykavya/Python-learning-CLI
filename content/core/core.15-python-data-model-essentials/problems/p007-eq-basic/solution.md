## Approach

Python calls `a.__eq__(b)` for `a == b`. Returning `NotImplemented` says "I do not know this type"; Python then tries `b.__eq__(a)`, and if that also declines, it answers `False`. `!=` is derived from `__eq__` automatically.

## Code

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)
```

## Complexity

O(1).

## Another way

Compare with `self.__dict__ == other.__dict__` (works but couples equality to every attribute) or let a dataclass generate `__eq__` (later section).
