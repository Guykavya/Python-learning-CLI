## Hint 1

Both are decorators with arguments, so you need three levels: factory → `decorate(func)` → `wrapper(*args, **kwargs)`.
Where do `types`, `low` and `high` come from inside the wrapper?

## Hint 2

How do you get the argument number together with the argument and its wanted type? Try
`enumerate(zip(args, types), start=1)`.

## Hint 3

```
wrapper(*args, **kwargs):
    if len(args) != len(types): raise TypeError(...)
    for i, (arg, wanted) in enumerate(zip(args, types), start=1):
        if not isinstance(arg, wanted): raise TypeError(...)
    return func(*args, **kwargs)
```
`in_range` is the same shape, with `isinstance(arg, (int, float)) and not (low <= arg <= high)`.
