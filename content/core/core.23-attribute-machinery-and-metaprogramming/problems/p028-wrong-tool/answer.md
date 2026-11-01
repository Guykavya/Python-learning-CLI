**A. Use `@dataclass`.**

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
```

Costs of the metaclass: (1) tools cannot see the fields. An IDE and a type checker do not know
that `Point(1, 2)` takes two arguments or that `p.x` exists, so there is no completion and no
error for `Point(1, 2, 3)`; the extra value is even silently dropped by `zip`, and `Point(1)`
leaves `y` unset until it fails later with `AttributeError`. (2) It is code the team must
maintain and test (no keyword arguments, no defaults, no `__hash__` handling: defining `__eq__`
sets `__hash__` to `None` and nobody notices), while `@dataclass` is standard, documented and
already handles defaults, ordering, `frozen` and `__slots__`. A metaclass also spreads: every
subclass and every class mixed with another metaclass inherits it (metaclass conflicts).

**B. Use `property`.**

```python
@property
def full_name(self):
    return f"{self.first} {self.last}"

@property
def age(self):
    return 2026 - self.birth_year
```

Costs: (1) the attributes are invisible: they are not in `dir()`, the class has no docstring for
them, and the IDE cannot complete `p.full_name`. (2) The logic for unrelated attributes is piled
into one `if` chain that grows with every new attribute.

**The hidden bug (B)**: `return None` for every other name. A typo like `p.frist` returns `None`
instead of raising `AttributeError`, so the bug travels far before it shows up (for example
`p.frist.upper()` fails somewhere else with a confusing message). `hasattr(p, "anything")` is
always `True`, and tools that probe special names with `hasattr`/`getattr`, like `copy` or
`pickle`, can get `None` and break or crash. A `__getattr__` must raise `AttributeError` for names
it does not handle.

**C. Use `__init_subclass__`.**

```python
class Exporter:
    registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "extension" not in vars(cls):
            raise TypeError(f"{cls.__name__} must define extension")
        Exporter.registry[cls.extension] = cls
```

Costs of the metaclass: (1) a metaclass conflict appears as soon as someone combines `Exporter`
with another class that has a metaclass (for example an `ABC`), even though the job never needed
control over class creation. (2) `if bases:` is fragile and hard to read: it is a trick to skip the
base class, while `__init_subclass__` runs only for subclasses by design. Also the registry is a
global dict; a class attribute keeps it next to the code that fills it. A class decorator
(`@register("csv")`) would also work and is the most explicit option.

**When a metaclass is justified.** When you need to control the *class object itself*, not only
the class creation. An enum is the classic case: `len(Color)`, `for c in Color`, `Color(2)` and
`Color.RED = 5` being refused are operations **on the class**, so they need `__len__`,
`__iter__`, `__call__` and `__setattr__` defined on the metaclass. Another case is `__prepare__`,
when the class body must run in a special namespace (for example to detect a name defined twice).
Neither `__init_subclass__` nor a decorator can do this.
