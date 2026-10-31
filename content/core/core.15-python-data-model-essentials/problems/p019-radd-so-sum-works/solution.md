## Approach

`sum` starts with `0`, so `0 + v1` must work. `__radd__` is called with the left operand as `other`; accepting only `0` keeps the operator honest.

## Code

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __repr__(self):
        return f"Vector({self.x!r}, {self.y!r})"

    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        if isinstance(other, (int, float)) and not isinstance(other, bool) and other == 0:
            return Vector(self.x, self.y)
        return NotImplemented
```

## Complexity

O(1) per addition; `sum` of n vectors is O(n).

## Another way

Use `sum(vs, Vector(0, 0))`: with an explicit start value, no `__radd__` is needed.
