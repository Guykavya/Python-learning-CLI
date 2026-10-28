## Hint 1

Split the job in two. First write a helper `matches(value, hint)` that answers True or False for
one value and one hint. Then the decorator only has to loop over the bound arguments and call
it. What does `typing.get_origin` return for `int`, for `list[int]`, and for `int | None`?

## Hint 2

`get_origin(int)` is `None` (a plain class: use `isinstance`). `get_origin(list[int])` is `list`
(check the outer class). For a union the origin is `typing.Union` or `type(int | str)`: loop
over `get_args(hint)` and call `matches` again for each member. Compute the hints and the
signature once, at decoration time.

## Hint 3

```
UNION_ORIGINS = (typing.Union, type(int | str))

matches(value, hint):
    origin = get_origin(hint)
    if origin is None: return isinstance(value, hint)
    if origin in UNION_ORIGINS: return any(matches(value, m) for m in get_args(hint))
    return isinstance(value, origin)

typechecked(func):
    hints = get_type_hints(func); sig = signature(func)
    @wraps(func)
    wrapper(*args, **kwargs):
        for param, value in sig.bind(*args, **kwargs).arguments.items():
            if param in hints and not matches(value, hints[param]): raise TypeError(...)
        result = func(*args, **kwargs)
        if "return" in hints and not matches(result, hints["return"]): raise TypeError(...)
        return result
```
