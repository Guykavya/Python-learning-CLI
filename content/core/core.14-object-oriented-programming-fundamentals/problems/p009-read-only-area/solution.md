## Approach

Store only what cannot be computed: the radius (chapter section 8). Everything that follows from it
is a read-only property, computed on each read, so it can never be out of date.

A property defined with only `@property` (a getter) has no setter. Assigning to it raises
`AttributeError: property 'area' of 'Circle' object has no setter` (Python 3.11 and newer). That is exactly the "read-only"
behaviour we want, for free.

The starter shows the trap: it saves `self.diameter` and `self.area` in `__init__`. Once `area` is a
property, that line itself would raise `AttributeError`, and without properties the saved numbers go
stale when the radius changes.

## Code

```python
import math


class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value <= 0:
            raise ValueError("radius must be positive")
        self._radius = value

    @property
    def diameter(self):
        return 2 * self.radius

    @property
    def area(self):
        return math.pi * self.radius ** 2
```

## Complexity

O(1) for every property.

## Another way

You could give `diameter` a setter too (`self.radius = value / 2`), so it is a second, checked way to
change the size, like `fahrenheit` in p008. For `area` a setter is possible (`sqrt(value / pi)`) but
unusual. If computing a value were slow, `functools.cached_property` would compute it once and store
it, but then it would not follow later radius changes.
