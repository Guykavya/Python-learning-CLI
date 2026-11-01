# Build a record class with `type()`

A `class` statement is a convenient way to call `type(name, bases, namespace)`: Python runs the
body, collects the names it defines into a dict, and passes that dict to `type`. You can call
`type` yourself to create a class whose name and fields are only known at run time (from a
config file, a database table, a CSV header).

Copy `starter.py` to `solution.py` and write `make_record_class(name, fields)`, where `fields`
is a list or tuple of attribute names. Build the class with **`type(name, (), namespace)`**. It
must have:

- `__name__` and `__qualname__` equal to `name`;
- `__slots__` equal to `tuple(fields)` (so instances have no `__dict__`, and an unknown
  attribute cannot be added);
- `__init__(self, *values)` that takes exactly one value per field, in order, and raises
  `TypeError` mentioning the expected count otherwise;
- `__repr__` giving `Name(field=repr(value), ...)`;
- `__eq__`: equal when `other` has **the same class** and equal values; for any other type return
  `NotImplemented` (so `Point(1, 2) == (1, 2)` is `False`, and a `Vector` with the same fields is
  not equal to a `Point`).

Later changes to the caller's `fields` list must not affect the class.

**Example**

```python
Point = make_record_class("Point", ["x", "y"])
p = Point(3, 4)
p                       # Point(x=3, y=4)
p == Point(3, 4)        # True
Point.__slots__         # ('x', 'y')
p.z = 1                 # AttributeError (no __dict__, 'z' is not a slot)
Point(1)                # TypeError: Point expects 2 values (x, y), got 1
```
