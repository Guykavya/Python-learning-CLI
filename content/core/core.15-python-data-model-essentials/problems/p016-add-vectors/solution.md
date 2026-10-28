## Approach

`v + w` is `v.__add__(w)`. Build and return a new `Vector`. Returning `NotImplemented` (never raising `TypeError` yourself) lets Python try the other operand's `__radd__` and produce the standard error message.

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

    def __sub__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x - other.x, self.y - other.y)
```

## Complexity

O(1).

## Another way

Return `type(self)(...)` so a subclass of `Vector` adds into its own type.
