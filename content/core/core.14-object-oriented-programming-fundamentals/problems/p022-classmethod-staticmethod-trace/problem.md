# Trace: classmethod and staticmethod through subclasses

A `classmethod` receives a class as its first argument, `cls`. **Which** class? The one you called it
on, or the class of the object you called it on. A `staticmethod` receives nothing extra at all. Read
the program and work out what it prints.

```python
class Shape:
    sides = 0
    made = []

    def __init__(self, label):
        self.label = label

    @classmethod
    def describe(cls):
        return f"{cls.__name__} has {cls.sides} sides"

    @classmethod
    def create(cls, label):
        cls.made.append(cls.__name__)
        return cls(label)

    @staticmethod
    def unit():
        return "cm"

    def info(self):
        return f"{self.label}: {self.describe()} in {self.unit()}"


class Triangle(Shape):
    sides = 3


class Square(Shape):
    sides = 4

    @staticmethod
    def unit():
        return "m"


print(Shape.describe())
print(Triangle.describe())
t = Triangle("t1")
print(t.describe())

s = Square.create("s1")
print(type(s).__name__, s.label)
print(s.info())
print(t.info())
print(Shape.unit(), t.unit(), s.unit())

x = t.create("t2")
print(type(x).__name__, Shape.made)

Triangle.sides = 30
print(x.describe(), Shape.describe())
```

Write every printed line in `answer.txt`, one per line.

Facts you need:

- `Triangle.describe()` passes `cls = Triangle`. `t.describe()` passes `cls = type(t)`, also `Triangle`.
  Inside `info`, `self.describe()` works the same way: `cls` is the class of `self`.
- `cls.__name__` is the class name as text, for example `"Triangle"`.
- `cls.sides` and `cls.made` are normal attribute lookups on the class: if the class does not define
  the name itself, Python looks in its parent class.
- A staticmethod is found by the normal lookup too (`self.unit()` finds the subclass's version first),
  but it gets no `self` and no `cls`.
- `type(obj).__name__` is the name of the object's class. A list prints like `['a', 'b']`.

## Example of the format

```python
print(Square.describe())
```

prints

```text
Square has 4 sides
```
