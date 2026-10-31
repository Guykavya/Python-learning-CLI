# Trace: which abstract classes can be instantiated?

An abstract base class refuses to build objects until **every** abstract method has been overridden
somewhere in the subclass chain. `register()` adds a class as a *virtual* subclass, which changes what
`isinstance` says, but nothing else. Trace this program and write its output in `answer.txt`.

```python
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self):
        return 0

    @abstractmethod
    def name(self):
        ...

    def describe(self):
        return f"{self.name()} has area {self.area()}"


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side * self.side


class NamedSquare(Square):
    def name(self):
        return "square"


class Triangle(Shape):
    def area(self):
        return super().area() + 6

    def name(self):
        return "triangle"


class Blob:
    def area(self):
        return 1

    def name(self):
        return "blob"


def make(cls, *args):
    try:
        obj = cls(*args)
    except TypeError:
        print(cls.__name__, "-> cannot instantiate")
        return None
    print(cls.__name__, "-> ok")
    return obj


make(Shape)
make(Square, 2)
sq = make(NamedSquare, 3)
tri = make(Triangle)
print(sq.describe())
print(tri.describe())
print(sorted(Shape.__abstractmethods__))
print(sorted(Square.__abstractmethods__))
print(sorted(NamedSquare.__abstractmethods__))
print(isinstance(sq, Shape), isinstance(Blob(), Shape))
Shape.register(Blob)
blob = make(Blob)
print(isinstance(blob, Shape), issubclass(Blob, Shape))
print(Shape in Blob.__mro__, hasattr(blob, "describe"))
print(Shape.area(sq))
```

Facts you need:

- `cls.__abstractmethods__` is a `frozenset` with the names of the abstract methods that are still
  not overridden. A class can be instantiated only when it is empty. `sorted()` turns it into a list.
- An abstract method can have a body. A subclass can call it with `super()`, or anybody can call it
  through the class.
- `make` prints exactly one line per call.

## Example of the format

```python
print(sorted(frozenset({"b", "a"})), isinstance(3, int))
```

prints

```text
['a', 'b'] True
```
