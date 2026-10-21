## Hint 1

How do you pass along 'whatever arguments I received' to `func`? What do the stars do in a call?

## Hint 2

Build a list of strings: `repr(a)` for each positional, `f"{k}={v!r}"` for each keyword. Then `", ".join(parts)`.

## Hint 3

```
result = func(*args, **kwargs)        # call once, keep the result
parts = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
return f"{func.__name__}({', '.join(parts)}) -> {result!r}"
```
