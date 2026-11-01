# Lock attributes after `__init__`

`obj.name = value` calls `type(obj).__setattr__(obj, "name", value)`, and `del obj.name` calls
`__delattr__`. Override them and you control every write and delete, including the ones inside
`__init__`. To really store a value from inside these hooks you must go around them with
`object.__setattr__(self, name, value)`; writing `self.name = value` there would call your hook
again.

Copy `starter.py` to `solution.py` and write a base class `Locked`:

- `Locked.__init__(self, **fields)` stores each keyword as an attribute and then **locks**
  this object. Subclasses call it with `super().__init__(...)`.
- Until the object is locked, normal assignment (`self.label = ...`) works.
- Once locked, **any** assignment (to an old or a new name, also via `setattr`) raises
  `AttributeError` whose message names the attribute, and the old value stays.
- `del obj.name` always raises `AttributeError` naming the attribute.
- Calling `__init__` again on a locked object raises `AttributeError` and changes nothing.
- `repr(obj)` is `ClassName(field=value, ...)` with the fields in the order they were stored,
  values shown with `repr`, and no trace of the lock flag.

The lock belongs to **each object**, not to the class: creating a second object must still work.

**Example**

```python
class Point(Locked):
    def __init__(self, x, y):
        super().__init__(x=x, y=y)

p = Point(1, 2)
p.x          # 1
repr(p)      # 'Point(x=1, y=2)'
p.x = 10     # AttributeError: cannot set 'x': Point is locked
del p.y      # AttributeError: cannot delete 'y': Point is locked
Point(3, 4)  # works: a new object starts unlocked
```
