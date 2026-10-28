## Approach

`Callable[[float], str]` has no way to name a parameter or to mark one keyword-only. A **callback protocol** puts the exact signature in the `__call__` method of a Protocol. Any function with the same parameter names, kinds, and compatible types is accepted; so is any instance of a class with such a `__call__`. The two functions `fixed` and `percent` are written to match that signature exactly, including the bare `*` that makes `precision` keyword-only.

`format_all` takes the `precision` and forwards it by keyword: `fmt(v, precision=precision)`. A keyword-only parameter cannot be passed positionally.

The number formatting uses a nested replacement field: `f"{value:.{precision}f}"` takes the number of digits from the variable.

## Code

```python
from collections.abc import Iterable
from typing import Protocol


class Formatter(Protocol):
    def __call__(self, value: float, *, precision: int = 2) -> str: ...


def fixed(value: float, *, precision: int = 2) -> str:
    return f"{value:.{precision}f}"


def percent(value: float, *, precision: int = 2) -> str:
    return f"{value * 100:.{precision}f}%"


def format_all(values: Iterable[float], fmt: Formatter, precision: int = 2) -> list[str]:
    return [fmt(v, precision=precision) for v in values]
```

## Complexity

`fixed`, `percent`: O(1). `format_all`: O(n) calls of `fmt`.

## Another way

You could use `Callable[..., str]` (anything goes, nothing is checked) or `Callable[[float], str]` (no `precision` at all). Both are simpler and both lose information. For code that needs callbacks with keyword-only arguments, defaults or `*args`, the callback protocol is the precise tool. For callbacks with positional parameters only, `Callable[[float, int], str]` is still the best choice.
