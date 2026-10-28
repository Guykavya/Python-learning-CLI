# Decorators that receive classes

A decorator receives whatever is below it. Usually that is a function, but it can be a **class**.
Class decorators are a lightweight way to register plug-ins or add methods without inheritance.
Write two things in `solution.py`.

**`Registry`**: an object that is itself a decorator for classes.

- `reg = Registry()`. Each registry has its own storage.
- `@reg` above a class registers it under `cls.__name__.lower()`.
- `@reg(name="x")` above a class registers it under `"x"`. So `reg.__call__` must handle both:
  called with the class directly, or called with only `name=` and then returning the real decorator.
- In both forms the class is **returned unchanged**, and the class gets the attribute
  `registered_name` set to the name used.
- A name that is already taken raises `ValueError` and leaves the registry as it was.
- `reg["x"]` returns the class; an unknown name raises `KeyError` whose message names the key.
  `"x" in reg`, `len(reg)` (number of classes) and `reg.names()` (sorted list of names) work too.

**`auto_repr(cls)`**: a class decorator that gives the class a `__repr__`. The class lists its
field names in a class attribute `_fields = ("x", "y")`. The repr is `ClassName(x=1, y='a')`:
the **actual** class name of the object (`type(self).__name__`) and `repr` of each current value.
It returns the class.

Both decorators can be stacked.

**Example**

```python
reg = Registry()

@reg
class Dog: ...

@reg(name="kitty")
class Cat: ...

reg.names()          # ['dog', 'kitty']
reg["kitty"] is Cat  # True

@auto_repr
class Point:
    _fields = ("x", "y")
    def __init__(self, x, y):
        self.x, self.y = x, y

Point(1, 2)          # Point(x=1, y=2)
```
