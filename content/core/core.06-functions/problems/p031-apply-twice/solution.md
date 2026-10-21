## Approach

`func` is an ordinary name whose value is a function. `func(value)` calls it; feeding that result into `func` again gives the answer.

## Code

```python
def apply_twice(func, value):
    """Return func(func(value))."""
    return func(func(value))
```

## Complexity

Two calls of `func`.

## Another way

A loop that applies `func` a given number of times generalises this:
`for _ in range(times): value = func(value)`.
