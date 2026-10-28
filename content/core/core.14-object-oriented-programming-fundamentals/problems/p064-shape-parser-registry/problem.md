# Parse shapes with a class registry

A drawing tool reads lines like `circle 2` or `rect 3 4` and turns each into a shape object. Instead
of a long `if kind == "circle": ... elif ...` chain, every shape class **registers** itself in a dict,
and the parser just looks the kind up. A new shape then needs no change to the parser at all.

In `solution.py` write:

### The shapes

- `Shape(ABC)` with:
  - class attributes `kind = ""` and `n_args = 0` (subclasses set them);
  - abstract method `area()`;
  - `describe()` returning `f"{self.kind} area={self.area():.2f}"`;
  - classmethod `from_args(cls, args)`: `args` is a list of strings. Convert each to `float`; a part
    that is not a number raises `ValueError(f"not a number: {text!r}")` (chained `from` the
    `float()` error). If `len(args) != cls.n_args`, raise
    `ValueError(f"{cls.kind} needs {cls.n_args} number(s), got {len(args)}")` (check the count
    **first**). If any number is `<= 0`, raise `ValueError("sizes must be positive")`. Otherwise
    return `cls(*numbers)`.
- `Circle(r)`: kind `"circle"`, 1 number, area `math.pi * r * r`.
- `Rect(w, h)`: kind `"rect"`, 2 numbers, area `w * h`.
- `Square(side)`: a subclass of `Rect`, kind `"square"`, 1 number. It calls
  `super().__init__(side, side)`.

### The registry

- `SHAPES = {}`: a module-level dict, kind -> class.
- `register_shape(cls)`: a **class decorator**. It stores `SHAPES[cls.kind] = cls` and returns `cls`.
  If the kind is already registered, raise `ValueError(f"shape {cls.kind!r} is already registered")`.
  Use it on `Circle`, `Rect` and `Square` (`@register_shape` above the `class` line).

### The exceptions

- `ShapeError(Exception)`.
- `UnknownShapeError(ShapeError)`: attribute `kind`; message `f"unknown shape {kind!r}"`.
- `BadShapeLine(ShapeError)`: attributes `line_no`, `line`, `reason`; message
  `f"line {line_no}: {reason}"`.

### The parser

- `parse_shape(text)`: split on whitespace; the first word, **lowercased**, is the kind, the rest are
  the numbers. Look the kind up in `SHAPES`; on `KeyError` raise `UnknownShapeError(kind)` **from**
  the `KeyError`. Then return `cls.from_args(rest)`. An empty text raises
  `ValueError("empty shape line")`.
- `parse_shapes(lines)`: `lines` is any iterable of strings (a list, an open file). Number the lines
  from 1. Skip lines that are blank or whose first non-space character is `#`. Return the list of
  shapes. On the first bad line, raise `BadShapeLine(line_no, line.strip(), str(err))` **from** the
  original error (`ValueError` or `UnknownShapeError`).
- `parse_all(lines)`: like `parse_shapes`, but it does not stop at the first bad line. It collects a
  `BadShapeLine` (each chained from its cause) for **every** bad line, and if there are any, raises
  `ExceptionGroup(f"{n} bad line(s)", errors)`. Otherwise it returns the shapes.

## Example

```python
parse_shape("circle 2").describe()       # 'circle area=12.57'
parse_shape("RECT 3 4").describe()       # 'rect area=12.00'
type(parse_shape("square 2")) is Square  # True; and isinstance(..., Rect) is True too

parse_shape("hexagon 1")       # UnknownShapeError: unknown shape 'hexagon'   (__cause__ is a KeyError)
parse_shape("rect 3")          # ValueError: rect needs 2 number(s), got 1
parse_shape("circle abc")      # ValueError: not a number: 'abc'
parse_shape("circle -1")       # ValueError: sizes must be positive

text = ["# my drawing", "circle 1", "", "rect 2 x"]
parse_shapes(text)             # BadShapeLine: line 4: not a number: 'x'

@register_shape
class Triangle(Shape):          # a new shape: the parser needs no change
    kind, n_args = "triangle", 2
    def __init__(self, base, height):
        self.base, self.height = base, height
    def area(self):
        return self.base * self.height / 2

parse_shape("triangle 3 4").area()   # 6.0
```
