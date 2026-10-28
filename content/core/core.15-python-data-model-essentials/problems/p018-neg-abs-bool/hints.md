## Hint 1

Which special method does `abs(v)` call? What should it return: a Vector or a number?

## Hint 2

`bool(v)` is `True` if either coordinate is non zero. Without `__bool__` and `__len__`, every object is truthy; that is why the starter fails.

## Hint 3

```
__neg__: Vector(-x, -y)
__pos__: Vector(x, y)          # a new object
__abs__: math.hypot(x, y)      # a float
__bool__: return x != 0 or y != 0
```
