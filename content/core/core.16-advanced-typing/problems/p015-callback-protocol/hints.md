## Hint 1

What does the `*` in `def f(value, *, precision=2)` do to the parameter after it? How would a caller have to pass `precision`? Why is this impossible to say with `Callable[[float], str]`?

## Hint 2

For the number formatting, an f-string can take the number of digits from a variable: `f"{value:.{precision}f}"`. `percent` is the same after multiplying by 100, and with `%` at the end. `format_all` calls `fmt(v, precision=precision)`: the keyword form is required, because the parameter is keyword-only.

## Hint 3

```
class Formatter(Protocol):
    def __call__(self, value: float, *, precision: int = 2) -> str: ...

fixed(value, *, precision=2):    return f"{value:.{precision}f}"
percent(value, *, precision=2):  return f"{value * 100:.{precision}f}%"
format_all(values, fmt, precision=2):  [fmt(v, precision=precision) for v in values]
```
