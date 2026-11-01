# Classify attributes without triggering them

When you write `obj.name`, Python first finds `name` in the classes of the MRO, and *what kind
of object it finds there* decides everything: a **data descriptor** beats the instance
dictionary, a **non-data descriptor** loses to it, and a plain value is just returned.

Write a small inspection tool that answers "what kind of class attribute is this?" **without
running it**. Calling `getattr(cls, name)` is not allowed: it would run a descriptor's
`__get__` (a property on the metaclass, a `cached_property`, a `__get__` that counts or raises,
or a metaclass `__getattr__` that invents attributes).

Copy `starter.py` to `solution.py` and write:

- `find_owner(cls, name)`: the first class in `cls.__mro__` whose own `__dict__` contains
  `name`, or `None` if no class has it.
- `classify(cls, name)`: returns one of four strings, based on the raw object stored under
  `name` in the owner's `__dict__`:
  - `"data descriptor"` if its **type** defines `__set__` or `__delete__` (properties, slots, your own validators)
  - `"non-data descriptor"` if its type defines `__get__` only (functions, `classmethod`, `staticmethod`, `cached_property`)
  - `"plain"` for any other object (numbers, strings, lists, nested classes, `None`)
  - `"missing"` if no class in the MRO has the name
- `describe(cls)`: a dict from each name defined in `cls`'s **own** `__dict__` that does not
  start with `__` to its classification, in definition order.

Two rules the tests check:

1. The descriptor protocol is looked up on the **type** of the object, never on the object
   itself. An object that merely *has an attribute* called `__set__` in its own dict is not a
   descriptor.
2. Only the MRO of `cls` counts. Attributes that exist only on the metaclass, or that a
   metaclass `__getattr__` invents, are `"missing"`.

**Example**

```python
class Base:
    kind = "base"
    def hello(self):
        return "hi"

class Point(Base):
    __slots__ = ("x",)
    @property
    def size(self):
        return 1

classify(Point, "x")       # 'data descriptor'      (a slot)
classify(Point, "size")    # 'data descriptor'      (property defines __set__)
classify(Point, "hello")   # 'non-data descriptor'  (found in Base)
classify(Point, "kind")    # 'plain'
classify(Point, "nope")    # 'missing'
find_owner(Point, "hello") # <class 'Base'>
describe(Point)            # {'x': 'data descriptor', 'size': 'data descriptor'}
```
