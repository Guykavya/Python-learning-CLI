# Your first dataclasses

A class that mostly **holds data** needs the same boilerplate every time: `__init__`, `__repr__`
and `__eq__`. The decorator `@dataclass` writes them for you from the **annotated names** in the
class body:

```python
from dataclasses import dataclass

@dataclass
class Dog:
    name: str
    age: int = 1        # a field with a default value
```

Fields with defaults must come after fields without defaults. The annotations are hints only;
Python does not check the types.

Write two dataclasses in `solution.py`. The starter has a hand-written `Point`: replace it.

- `Point` with `x: int` and `y: int = 0`, and a method `distance_to_origin()` returning
  `(x**2 + y**2) ** 0.5`.
- `Product` with `name: str`, `price: float` and `qty: int = 0`, and a method `total()` returning
  `price * qty`.

Do not write `__init__`, `__repr__` or `__eq__` yourself.

**Example**

```python
p = Point(3, 4)
p                      # Point(x=3, y=4)
p == Point(3, 4)       # True
p.distance_to_origin() # 5.0
Product("pen", 2.5, 4) # Product(name='pen', price=2.5, qty=4)
```
