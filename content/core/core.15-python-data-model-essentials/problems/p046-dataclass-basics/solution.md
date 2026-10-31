## Approach

`@dataclass` inspects `__annotations__` of the class and generates `__init__`, `__repr__` and `__eq__` (and `__match_args__`). Methods you write yourself are kept as they are. Because it is just a class decorator (previous section), what you get is an ordinary class.

## Code

```python
from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int = 0

    def distance_to_origin(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5


@dataclass
class Product:
    name: str
    price: float
    qty: int = 0

    def total(self):
        return self.price * self.qty
```

## Complexity

O(1) per method call; no cost compared with a handwritten class.

## Another way

`collections.namedtuple` or `typing.NamedTuple` also give you a repr and equality, but the result is an immutable tuple (you can index and unpack it). A dataclass is a normal mutable class.
