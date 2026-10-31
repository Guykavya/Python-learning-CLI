# Where is this attribute defined?

When you write `obj.save()`, Python walks the classes in `type(obj).__mro__` from left to right and
uses the **first** class whose own namespace (`vars(klass)`) contains `save`. In a big hierarchy it
is often hard to see which class that is. Write two small tools that answer the question.

In `solution.py` write:

### `defined_in(cls, name)`

Return the **class** in `cls.__mro__` that defines `name` in its own `vars()`, the first one in
MRO order. Return `None` if no class in the MRO defines it.

- If `cls` is not a class, raise `TypeError("defined_in() needs a class")`.
  (`isinstance(cls, type)` is `True` exactly for classes.)
- Only names defined **in a class body** (or assigned to the class later) count. Attributes that
  only instances have, like `self.name` set in `__init__`, are not in any class's `vars()`.
- `object` is the last class in every MRO, so names like `"__init__"` or `"__repr__"` are found at
  the latest in `object`.

### `all_definitions(cls, name)`

Return a list with the **names** (strings) of every class in `cls.__mro__` that defines `name`,
in MRO order. The first one is the definition that is used; the others are overridden by it.
Return `[]` if nobody defines it. Same `TypeError` rule as above
(message `"all_definitions() needs a class"`).

## Example

```python
class Base:
    kind = "base"
    def save(self): ...
    def load(self): ...

class Left(Base):
    def save(self): ...

class Right(Base):
    kind = "right"
    def load(self): ...

class Child(Left, Right):
    pass

# Child.__mro__ is (Child, Left, Right, Base, object)
defined_in(Child, "save")        # Left
defined_in(Child, "load")        # Right   (Right comes before Base in the MRO)
defined_in(Child, "kind")        # Right
defined_in(Child, "missing")     # None
defined_in(Child, "__init__")    # object
all_definitions(Child, "load")   # ['Right', 'Base']
all_definitions(Child, "__init__")  # ['object']
defined_in(Child(), "save")      # TypeError: defined_in() needs a class
```
