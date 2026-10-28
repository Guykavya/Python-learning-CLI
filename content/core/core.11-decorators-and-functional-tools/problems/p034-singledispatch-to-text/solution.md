## Approach

`singledispatch` keeps a registry from types to functions. On each call it looks at
`type(value)` and walks up its parent classes until it finds a registered one. `bool`'s parents
are `int` and then `object`, so if only `int` is registered, `True` is printed by the `int`
function. Registering `bool` makes the lookup stop there first.

Containers call `to_text` on their parts, so the dispatch happens again for each part. That is
recursion through the dispatcher, and it is why `[[1], [True]]` works with no extra code.

## Code

```python
from functools import singledispatch


@singledispatch
def to_text(value):
    raise TypeError(f"cannot convert {type(value).__name__}")


@to_text.register(int)
def _(value):
    return str(value)


@to_text.register(bool)
def _(value):
    return "yes" if value else "no"


@to_text.register(float)
def _(value):
    return f"{value:.2f}"


@to_text.register(str)
def _(value):
    return f'"{value}"'


@to_text.register(type(None))
def _(value):
    return "null"


@to_text.register(list)
def _(value):
    return "[" + ", ".join(to_text(item) for item in value) + "]"


@to_text.register(tuple)
def _(value):
    inner = ", ".join(to_text(item) for item in value)
    if len(value) == 1:
        inner += ","
    return "(" + inner + ")"


@to_text.register(dict)
def _(value):
    pairs = [f"{to_text(k)}: {to_text(v)}" for k, v in value.items()]
    return "{" + ", ".join(pairs) + "}"
```

## Complexity

O(total size of the value): every item is visited once. Dispatch itself is cached by type, so it
is fast after the first call for each type.

## Another way

One function with an `if isinstance(value, bool): ... elif isinstance(value, int): ...` chain.
It works, but the order of the checks matters (bool must come before int), and adding a new
type means editing the big function. With `singledispatch`, other code can add a type with
`@to_text.register(MyType)` without touching yours.

The registered functions are all called `_` because you never call them by name; only the
dispatcher calls them.
