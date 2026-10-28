# A callback Protocol with `__call__`

`Callable[[float], str]` is fine for simple callbacks, but it cannot say "this function also has
a keyword-only parameter `precision` with a default". For that you describe the callback with a
Protocol that has a `__call__` method. Any function (or any object with `__call__`) with that
exact signature fits.

In `solution.py` write:

```python
class Formatter(Protocol):
    def __call__(self, value: float, *, precision: int = 2) -> str: ...
```

and:

1. `fixed(value: float, *, precision: int = 2) -> str`: the number with `precision` digits after
   the decimal point. `fixed(3.14159)` is `'3.14'`, `fixed(3.14159, precision=0)` is `'3'`.
2. `percent(value: float, *, precision: int = 2) -> str`: the value times 100, with `precision`
   digits, and a `%` sign. `percent(0.256)` is `'25.60%'`, `percent(0.256, precision=0)` is `'26%'`.
3. `format_all(values: Iterable[float], fmt: Formatter, precision: int = 2) -> list[str]`: apply
   `fmt` to every value, **passing `precision` as a keyword argument** (`fmt(v, precision=precision)`).

The tests check that `fixed` and `percent` have the **same signature** as `Formatter.__call__`
(same parameter names, same kinds, same defaults, same hints), and that `format_all` also accepts
an object with a `__call__` method.

**Example**

```python
format_all([1, 2.5], fixed)                  # ['1.00', '2.50']
format_all([0.5, 0.123], percent, precision=1)   # ['50.0%', '12.3%']

class Brackets:
    def __call__(self, value: float, *, precision: int = 2) -> str:
        return "[" + fixed(value, precision=precision) + "]"

format_all([1], Brackets())                  # ['[1.00]']
```
