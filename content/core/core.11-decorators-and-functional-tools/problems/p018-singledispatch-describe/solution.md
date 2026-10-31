## Approach

`singledispatch` keeps a table from type to function. When `describe(x)` is called, it walks the class
hierarchy of `type(x)` and picks the closest registered type. `bool` inherits from `int`, so it needs its
own entry; with one, `True` finds `bool` before `int`. The list version calls `describe` on each item, so
nested values go to the right versions automatically.

## Code

```python
from functools import singledispatch


@singledispatch
def describe(x):
    return f"unknown: {x!r}"


@describe.register
def _(x: int):
    kind = "even" if x % 2 == 0 else "odd"
    return f"int {x} ({kind})"


@describe.register
def _(x: bool):
    return f"bool {x}"


@describe.register
def _(x: str):
    return f"text {x!r} of length {len(x)}"


@describe.register
def _(x: list):
    inner = ", ".join(describe(item) for item in x)
    return f"list of {len(x)}: [{inner}]"
```

## Complexity

O(1) per value plus the cost of building the text; a list costs the sum of its items.

## Another way

An `if isinstance(x, bool): ... elif isinstance(x, int): ...` chain works, but the order matters (bool must
come first) and every new type means editing the same function. With `singledispatch`, any other module
can add a version with `@describe.register(...)` without touching this one.
