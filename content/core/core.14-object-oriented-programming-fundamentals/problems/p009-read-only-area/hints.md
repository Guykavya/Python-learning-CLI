## Hint 1

Which of the three values should be stored, and which should be computed every time they are read?
If you stored `self.area` in `__init__`, what would `c.area` say after `c.radius = 3`?

## Hint 2

Give `radius` a getter and a setter, and let `__init__` assign `self.radius = radius` so the setter
checks it. Give `diameter` and `area` **only** a getter (`@property`). Assigning to a property with no
setter raises `AttributeError` automatically; you write nothing for that.

## Hint 3

```
import math

class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def radius(self): return self._radius

    @radius.setter
    def radius(self, value):
        if value <= 0: raise ValueError("radius must be positive")
        self._radius = value

    @property
    def diameter(self): return 2 * self.radius

    @property
    def area(self): return math.pi * self.radius ** 2
```
