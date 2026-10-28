## Approach

`trace` builds `wrapper` but never returns it, so `trace(add)` is `None` and the name `add` now holds
`None`. `print(add)` prints `None`. `add(2, 3)` tries to call `None`, which raises
`TypeError: 'NoneType' object is not callable`. The wrapper never runs, so `calling add` is never printed.

`quiet` returns its wrapper, so `mul(4, 5)` runs the wrapper. It prints `calling mul` and computes
`20`, but it throws the result away: there is no `return` in front of `func(*args)`. The wrapper returns
`None`, and `print` shows `None`. The wrapper was not made with `functools.wraps`, so `mul.__name__` is
`wrapper`.

## Output

```text
None
TypeError: 'NoneType' object is not callable
calling mul
None
wrapper
```

## Complexity

O(1).

## Another way

Check a decorator in two steps. First: does the decorator `return wrapper`? Second: does the wrapper
`return func(...)` (or a changed result)? Both returns are needed. A test that compares the decorated
function's result with the original catches the second bug at once.
