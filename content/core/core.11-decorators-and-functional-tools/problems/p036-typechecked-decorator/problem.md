# typechecked: enforce type hints at call time

Python does **not** check type hints when it runs your code: `def f(n: int)` happily accepts
`"7"`. A decorator can add that check.

Write a decorator `typechecked(func)` in `solution.py`. It uses two tools:

- `typing.get_type_hints(func)` returns a dict of the hints, for example
  `{"n": int, "name": str, "return": bool}`. A hint of `None` comes back as `type(None)`.
- `inspect.signature(func).bind(*args, **kwargs).arguments` gives the passed arguments by
  parameter name.

**Rules**

1. On each call, check every **passed** argument that has a hint. Parameters without a hint are
   not checked. Defaults that were not passed are not checked.
2. If an argument does not match, raise `TypeError` **before** calling the function. The message
   must contain the function name, the parameter name and the actual type name, for example:
   `area: argument 'w' must be int, got str`.
3. After the call, if there is a `"return"` hint, check the result the same way. The message
   names the function and the actual type, for example `area: return value must be int, got float`.
4. What "matches" means for each kind of hint:
   - a plain class (`int`, `str`, `list`, `type(None)` ...): `isinstance(value, hint)`.
   - a generic like `list[int]` or `dict[str, int]`: only the outer class is checked
     (`list`, `dict`). Use `typing.get_origin(hint)` to get it.
   - a union like `int | None` or `int | str`: the value matches if it matches **any** member.
     `typing.get_args(hint)` gives the members. A union's origin is either `typing.Union` or
     `type(int | str)`, depending on the Python version; accept both.
5. If the call itself does not fit the parameters, `bind` raises `TypeError`: let it go up.
6. Use `functools.wraps`. Your function is only tested on plain parameters (no `*args` or `**kwargs`).

**Example**

```python
@typechecked
def area(w: int, h: int = 1) -> int:
    return w * h

area(2, 3)        # 6
area("2", 3)      # TypeError: area: argument 'w' must be int, got str

@typechecked
def first(items: list[str], default: str | None = None):
    return items[0] if items else default

first(["a"])          # "a"
first(("a",))         # TypeError: ... 'items' ... got tuple
first([], None)       # None
```

Note: `bool` is a subclass of `int`, so `area(True)` passes the check. That is how `isinstance`
works, and it is fine here.
