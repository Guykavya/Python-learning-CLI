## Approach

The left operand gets the first chance (`__mul__`); only if it returns `NotImplemented` does Python try the right operand's reflected method (`__rmul__`). Because scaling is commutative, `__rmul__` can reuse `__mul__`.

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

    def __mul__(self, k):
        if not isinstance(k, (int, float)):
            return NotImplemented
        return Vector(self.x * k, self.y * k)

    def __rmul__(self, k):
        return self.__mul__(k)

    def __truediv__(self, k):
        if not isinstance(k, (int, float)):
            return NotImplemented
        return Vector(self.x / k, self.y / k)
```

## Complexity

O(1).

## Another way

Write `__rmul__ = __mul__` in the class body: it works here because the two operands play the same role.
