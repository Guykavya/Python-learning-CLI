## Approach

Each unary operator is a one-argument special method. `__bool__` must return a real `bool`.

## Code

```python
import math


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

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __pos__(self):
        return Vector(self.x, self.y)

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return self.x != 0 or self.y != 0
```

## Complexity

O(1).

## Another way

Implement `__bool__` as `return bool(abs(self))`; it reads well but computes a square root for nothing.
