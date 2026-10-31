# A circle with read-only computed properties

A circle is fully described by its radius. Its diameter and area **follow** from the radius, so it
makes no sense to set them on their own. A property with a getter and **no setter** is read-only:
Python raises `AttributeError` if someone tries to assign to it.

Write a class `Circle` in `solution.py`:

- `Circle(radius)` makes a circle.
- `c.radius` is a property. Reading gives the radius. Setting it to zero or a negative number
  raises `ValueError("radius must be positive")` and keeps the old radius. The constructor uses the
  same check. Store the value in `self._radius`.
- `c.diameter` is a **read-only** property: `2 * radius`.
- `c.area` is a **read-only** property: `math.pi * radius ** 2`.
- Assigning to `c.diameter` or `c.area` must raise `AttributeError` (a property without a setter does
  this for you).

**Example**

```python
c = Circle(2)
print(c.radius, c.diameter)    # 2 4
print(round(c.area, 2))        # 12.57
c.radius = 3
print(c.diameter)              # 6     (follows the new radius)
c.area = 100                   # AttributeError
c.radius = 0                   # ValueError: radius must be positive
```
