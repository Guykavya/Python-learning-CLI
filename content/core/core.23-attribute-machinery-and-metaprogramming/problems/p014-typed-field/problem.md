# A typed field descriptor

Python does not check types at run time: `p.x = "oops"` is accepted even if `x` should be an
`int`. A **data descriptor** can check every assignment, because `__set__` runs for
`p.x = value` before anything is stored.

Copy `starter.py` to `solution.py` and write the class `Typed`:

```python
class Point:
    x = Typed(int)
    y = Typed(int, float)          # several allowed types

    def __init__(self, x, y):
        self.x = x                 # goes through Typed.__set__, so it is checked too
        self.y = y
```

Rules:

1. `Typed(*types, allow_bool=False)`. At least one type is required and each must be a class:
   `Typed()` and `Typed("int")` raise `TypeError` when the field is created.
2. `__set_name__(self, owner, name)` remembers the field name (attribute `name`) and the class
   name (`owner.__name__`, the class where the field is written).
3. `__set__` checks with `isinstance` (so subclasses are accepted) and stores the value **per
   instance**. A wrong type raises `TypeError` with this message:

   ```
   Point.x must be int, got str
   Point.y must be int or float, got list
   ```

   The expected types are joined with `" or "` in the order they were given. The value is
   never converted (`"3"` is not turned into `3`), and a rejected value leaves the old one in place.
4. **`bool` is not `int` here.** `isinstance(True, int)` is `True` in Python (bool is a
   subclass of int), which is usually a bug for a field like `age`. So a `bool` value is
   rejected (`Point.x must be int, got bool`) unless `bool` is one of the types or the field
   was made with `allow_bool=True`.
5. `__get__`: on the class (`Point.x`) return the descriptor itself. On an instance return the
   stored value. If it was never set (or was deleted), raise **`AttributeError`** naming the
   field (for example `Point.x has not been set`), never `KeyError`, so `hasattr` and
   `getattr(obj, name, default)` keep working.
6. `__delete__`: `del p.x` removes the value; deleting an unset value raises `AttributeError`.

**Example**

```python
p = Point(1, 2.5)
p.x, p.y                 # (1, 2.5)
p.x = "3"                # TypeError: Point.x must be int, got str
p.x                      # still 1
p.y = True               # TypeError: Point.y must be int or float, got bool
Point.x.name             # 'x'
del p.x
hasattr(p, "x")          # False
```
