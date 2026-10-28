## Approach

`class Box[T]:` declares the type parameter `T` *inside the class statement*. It belongs to `Box` alone: no module-level `TypeVar` line, no shared global name, and the checker knows the variance on its own. A method can declare its own parameter the same way, `def map[U](...)`: `U` is solved at every call (`Box(5).map(str)` gives `U = str`, so the result is a `Box[str]`).

The syntax `[N: (int, float)]` makes `N` a **constrained** parameter (like `TypeVar("N", int, float)`); `[N: Sized]` without parentheses would be a **bound**. Python stores the parameters in `__type_params__` of the class or function, which is how the tests know you used the new syntax.

`__eq__` returns `NotImplemented` for a non-`Box`: that lets Python try the other side and finally say `False`. Defining `__eq__` removes the default `__hash__` (core.15), so `__hash__` is added.

## Code

```python
from collections.abc import Callable


class Box[T]:
    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value

    def map[U](self, func: Callable[[T], U]) -> "Box[U]":
        return Box(func(self.value))

    def __repr__(self) -> str:
        return f"Box({self.value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Box):
            return NotImplemented
        return bool(self.value == other.value)

    def __hash__(self) -> int:
        return hash(("Box", self.value))


def biggest[N: (int, float)](a: N, b: N) -> N:
    return b if b > a else a
```

## Complexity

All methods O(1) plus the cost of `func`.

## Another way

The old spelling gives the same types: `T = TypeVar("T")`, `class Box(Generic[T])`, `U = TypeVar("U")`. It works on every Python 3 version; the new syntax needs 3.12. For the `Box` itself a `@dataclass(frozen=True)` would write `__init__`, `__repr__`, `__eq__` and `__hash__` for you (but the repr would read `Box(value=5)`).
