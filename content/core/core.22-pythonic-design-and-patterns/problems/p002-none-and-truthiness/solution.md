## Approach

"Falsy" is not the same as "missing". Python treats `0`, `0.0`, `""`, `[]`, `{}`, `set()`, `None`
and `False` as false in an `if`. Use plain truthiness only when you really mean "nothing useful
here" for every one of them. When you mean "was a value given?", ask `is None`.

Booleans need care: `True == 1` and `False == 0`. So compare with `is True` / `is False`, and ask
for them **before** the check for zero (otherwise `False` would be called "zero").

## Code

```python
def describe(value):
    if value is None:
        return "missing"
    if value is True:
        return "yes"
    if value is False:
        return "no"
    if value == 0:
        return "zero"
    if value == "":
        return "empty text"
    if value == []:
        return "empty list"
    return f"value {value!r}"


def first_non_empty(values, default=None):
    for v in values:
        if v is not None:
            return v
    return default


def config_get(config, key, default):
    value = config.get(key)
    return default if value is None else value
```

## Complexity

`describe` and `config_get` are O(1) (one dictionary lookup). `first_non_empty` is O(n) and
stops at the first hit.

## Another way

`config_get` can use a sentinel to tell "missing" from "stored None": `config.get(key, None)`
cannot, but `value = config.get(key, _MISSING)` can. Here the statement says `None` also means
"use the default", so one `is None` test is enough. `first_non_empty` can be
`next((v for v in values if v is not None), default)`.
