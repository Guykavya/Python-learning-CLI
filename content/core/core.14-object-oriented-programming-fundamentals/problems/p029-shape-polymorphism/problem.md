# Shapes: one report for every kind

A drawing app must print a report about all shapes on the page. New kinds of shapes are added
every month, so the report code must **not** check which kind each shape is. It only calls
methods that every shape has. Write the classes and functions in `solution.py`.

**Classes**

- `Shape`: the base class. It has a class attribute `name = "shape"`, a method `area()` that raises
  `NotImplementedError`, and a method `describe()` that returns
  `f"{self.name} with area {self.area():.2f}"`.
- `Circle(r)`: `name = "circle"`, area `math.pi * r * r`.
- `Rectangle(w, h)`: `name = "rectangle"`, area `w * h`.
- `Square(side)`: a `Rectangle` whose width and height are both `side`; `name = "square"`.
  Build it by calling `super().__init__(side, side)`; do not write `area` again.
- `Triangle(a, b, c)`: `name = "triangle"`. Area by Heron's formula: `s = (a + b + c) / 2`,
  area `math.sqrt(s * (s - a) * (s - b) * (s - c))`. If the three sides cannot make a triangle
  (one side is equal to or longer than the other two together), raise `ValueError`.
- Every length must be above 0, otherwise `ValueError`. Store the lengths as attributes
  `r`, `w`, `h`, `side`, `a`, `b`, `c` (a square has `side`, `w` and `h`).

**Functions** (each takes a list of shapes; do not use `isinstance` or `type()` in them)

- `total_area(shapes)` returns the sum of the areas rounded to 2 decimals (`0` for an empty list).
- `largest(shapes)` returns the shape **object** with the biggest area. If two are equally big,
  return the first one. An empty list raises `ValueError`.
- `report(shapes)` returns a list of lines, biggest area first, numbered from 1:
  `"1. circle with area 12.57"`. Shapes with equal areas keep their order from the input.

**Example**

```python
shapes = [Rectangle(2, 3), Circle(2), Square(2), Triangle(3, 4, 5)]
total_area(shapes)        # 28.57
largest(shapes).name      # 'circle'
report(shapes)
# ['1. circle with area 12.57',
#  '2. rectangle with area 6.00',
#  '3. triangle with area 6.00',
#  '4. square with area 4.00']
Triangle(1, 2, 3)         # ValueError: these sides do not make a triangle
```
