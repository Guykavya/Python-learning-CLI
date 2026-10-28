- Writing `if isinstance(shape, Circle): ... elif isinstance(shape, Rectangle): ...` in the
  functions. Every new shape then needs a new branch, and `Hexagon` is silently skipped.
- Putting `name` only in `__init__` of some classes. Then `Square` may print "rectangle". A class
  attribute per class is simpler.
- Writing `area` again in `Square`. The inherited `Rectangle.area` already does it.
- Using `>=` in `largest`. On a tie that returns the last shape, not the first.
- Calling `shapes.sort(...)` in `report`. That reorders the caller's list. Use `sorted`.
- Checking only `a + b > c` for the triangle. With sides `(10, 2, 3)` that check passes, but the
  sides cannot make a triangle.
- Formatting the area with `round(area, 2)` in `describe`. `round(6.0, 2)` prints `6.0`, not `6.00`;
  use `:.2f`.
