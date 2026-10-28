## Hint 1

Which methods can `Shape` itself not write, because it does not know the shape? Those are the
abstract ones. Which method *can* `Shape` write, because it only needs the answers of the other two?

## Hint 2

```
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self): ...

    @abstractmethod
    def perimeter(self): ...

    def describe(self):
        return f"{type(self).__name__}: area {self.area():.2f}, perimeter {self.perimeter():.2f}"
```

You never write the `TypeError` yourself: `ABC` raises it when a class with abstract methods is called.
