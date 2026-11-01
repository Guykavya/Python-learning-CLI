# An enum from scratch

`enum.Enum` (core.15) looks like ordinary class syntax, yet `len(Color)`, `for c in Color` and
`Color(2)` work, and `Color.RED = 5` is refused. None of that is possible with a normal class:
these are operations **on the class object**, so they are defined on its metaclass. Build a
small version yourself.

Copy `starter.py` to `solution.py` and write a metaclass `EnumMeta` and a base class
`MiniEnum` (created with `metaclass=EnumMeta`) so that this works:

```python
class Color(MiniEnum):
    RED = 1
    GREEN = 2
    BLUE = 3

    def describe(self):
        return f"{self.name} is {self.value}"
```

**Which names are members?** Every name in the class body that does **not** start with `_`
and whose value is **not a descriptor** (its type has no `__get__`). So `describe` (a function),
properties, `classmethod`/`staticmethod` objects and `_private = 5` are *not* members. Find them
in the namespace the metaclass receives, never through annotations.

**Members.**

- Each member is an **instance** of the enum class: `type(Color.RED) is Color`.
- `Color.RED.name == "RED"`, `Color.RED.value == 1`; both are read-only.
- Members are immutable: setting or deleting **any** attribute on a member raises `AttributeError`.
- `repr(Color.RED) == "<Color.RED: 1>"` and `str(Color.RED) == "Color.RED"`.
- Methods from the class body work on members: `Color.GREEN.describe() == "GREEN is 2"`.
- Two members with an equal value raise `ValueError` when the class is created (the message names the second member).

**The class** (all defined on `EnumMeta`):

| Expression | Result |
|---|---|
| `list(Color)` | members in definition order |
| `len(Color)` | `3` |
| `Color(2)` | `Color.GREEN` (lookup by value, never a new object); unknown value: `ValueError("7 is not a valid Color")` |
| `Color["BLUE"]` | `Color.BLUE`; unknown name: `KeyError` |
| `Color.RED in Color` | `True` (only members are "in" the enum: `1 in Color` is `False`) |
| `Color.RED = 5`, `del Color.RED` | `AttributeError` (other new class attributes may be set freely) |
| `bool(Color)`, `bool(EmptyEnum)` | always `True` (a class is truthy, even with no members) |
| `class More(Color): ...` | `TypeError`: an enum that has members cannot be extended |

A subclass of an enum **without** members is allowed (useful to share methods).

**Example**

```python
Color(1) is Color.RED            # True
[c.name for c in Color]          # ['RED', 'GREEN', 'BLUE']
Color.RED.value = 10             # AttributeError
isinstance(Color.RED, Color)     # True
Color.RED == 1                   # False: a member is not its value
```
