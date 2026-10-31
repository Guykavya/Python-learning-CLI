## Hint 1

`3 * v`: which object's method does Python try first? What does `int` answer for a type it does not know? Which method on `Vector` is tried next?

## Hint 2

Write `__mul__` for the scalar case with a type check `isinstance(k, (int, float))`. Then `__rmul__` can simply do the same thing: `return self * k` (or `self.__mul__(k)`).

## Hint 3

```
def __mul__(self, k):
    if k is not int/float: return NotImplemented
    return Vector(self.x * k, self.y * k)
__rmul__ = same behaviour (multiplication by a number is commutative)
def __truediv__(self, k): check number; return Vector(self.x / k, self.y / k)
```
