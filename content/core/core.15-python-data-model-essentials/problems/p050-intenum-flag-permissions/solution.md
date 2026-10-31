## Approach

`Flag` builds on integers with one bit per member, so `|`, `&`, `^`, `~` and `in` are bit operations that return `Flag` objects. `needed in granted` is `(needed & granted) == needed`, which is exactly "all needed bits are granted". The empty flag `Permission(0)` is falsy.

`IntEnum` inherits from `int`: members behave like numbers (comparison, sorting, `max`), which a plain `Enum` deliberately refuses. The price is that they are also equal to plain ints, which can hide mistakes; use `IntEnum` only when the numeric behaviour is the point.

## Code

```python
from enum import Flag, IntEnum, auto


class Permission(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


def describe(perm):
    return "".join(
        letter if flag in perm else "-"
        for letter, flag in (("r", Permission.READ), ("w", Permission.WRITE), ("x", Permission.EXECUTE))
    )


def parse(text):
    if len(text) != 3:
        raise ValueError(f"expected 3 characters like 'rw-', got {text!r}")
    result = Permission(0)
    for char, expected, flag in zip(text, "rwx", (Permission.READ, Permission.WRITE, Permission.EXECUTE)):
        if char == expected:
            result |= flag
        elif char != "-":
            raise ValueError(f"bad character {char!r} in {text!r}")
    return result


def allows(granted, needed):
    return needed in granted


def highest(priorities):
    return max(priorities, default=None)
```

## Complexity

All functions are O(1) (three flags) except `highest`, which is O(n).

## Another way

`parse` could use `Permission(sum(...))` or a dict from letter to flag. `describe` can also iterate over the members (`for flag in Permission`) and use `flag.name[0].lower()` for the letter: shorter, but breaks if member names change.
