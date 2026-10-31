## Hint 1

What does every shape have, whatever its kind? A `name` and an `area()`. If `report` only uses
those two (and `describe()`, which uses them), does it ever need to know which class a shape is?
Where should `describe()` live so that you write it only once?

## Hint 2

`Square` is a rectangle with equal sides. If its `__init__` calls `super().__init__(side, side)`,
which attributes does it get for free, and which method does it not need to write? For the report,
`sorted(shapes, key=..., reverse=True)` keeps equal items in their original order.

## Hint 3

```
class Square(Rectangle):
    name = "square"
    __init__(side): super().__init__(side, side); self.side = side

total_area(shapes): round(sum of shape.area() for each shape, 2)

largest(shapes):
    if empty: raise ValueError
    best = shapes[0]
    for shape in the rest: if shape.area() > best.area(): best = shape
    return best

report(shapes):
    ordered = sorted(shapes, key=lambda s: s.area(), reverse=True)
    return [f"{i}. {s.describe()}" for i, s in enumerate(ordered, start=1)]
```
