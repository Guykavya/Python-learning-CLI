## Approach

`Shape` describes what every shape can do without saying how (chapter section 16):

- `area` and `perimeter` depend on the kind of shape, so `Shape` marks them `@abstractmethod` and
  gives them no real body.
- `describe` only needs the *answers* of those two, so `Shape` can write it once. When it runs on a
  `Square`, `self.area()` finds `Square.area` (section 10's template method again).

Because `Shape` inherits from `ABC`, Python checks at object-creation time that no abstract methods
are left. `Shape()` and a half-finished subclass both raise `TypeError`, long before anyone calls the
missing method.

## Code

```python
import math
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self):
        ...

    @abstractmethod
    def perimeter(self):
        ...

    def describe(self):
        return f"{type(self).__name__}: area {self.area():.2f}, perimeter {self.perimeter():.2f}"


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2

    def perimeter(self):
        return 4 * self.side


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

    def perimeter(self):
        return 2 * math.pi * self.radius
```

## Complexity

O(1) for every method.

## Another way

Without `abc`, a base method could `raise NotImplementedError`. That works, but the error appears only
when the missing method is **called**, maybe weeks later in production. With `ABC` the mistake shows the
moment the object is created. `Shape.__abstractmethods__` lists the names still missing.
