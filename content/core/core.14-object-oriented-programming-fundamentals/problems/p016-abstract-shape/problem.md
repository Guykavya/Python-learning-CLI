# An abstract Shape base class

"Shape" is an idea, not a real shape: you cannot compute the area of "a shape". An **abstract base
class** says which methods every real subclass **must** have. Python refuses to create an object of
a class that still has abstract methods, so a forgotten method is caught at once.

Write in `solution.py`:

- `Shape`, a subclass of `abc.ABC`, with two abstract methods, `area()` and `perimeter()` (use
  `@abstractmethod`), and one **concrete** method `describe()` that returns:

  `"<ClassName>: area <area>, perimeter <perimeter>"`, both numbers with 2 decimals.

  Get the class name with `type(self).__name__`. `describe` must call `self.area()` and
  `self.perimeter()`, so it works for every subclass.
- `Square(side)`, a subclass of `Shape`: area `side ** 2`, perimeter `4 * side`.
- `Circle(radius)`, a subclass of `Shape`: area `math.pi * radius ** 2`, perimeter `2 * math.pi * radius`.

`Shape()` must raise `TypeError`.

**Example**

```python
print(Square(3).describe())     # Square: area 9.00, perimeter 12.00
print(Circle(1).describe())     # Circle: area 3.14, perimeter 6.28
shapes = [Square(2), Circle(2)]
print(round(sum(s.area() for s in shapes), 2))   # 16.57
Shape()                         # TypeError: Can't instantiate abstract class Shape ...
```
