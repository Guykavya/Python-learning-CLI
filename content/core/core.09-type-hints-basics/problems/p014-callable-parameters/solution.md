## Approach

`apply_all` and `keep_if` are comprehensions that call the function they receive. `compose` and `make_adder` return a function, which is why their return hint is `Callable[[int], int]`. The inner function can use the outer function's variables (a closure), so no extra parameters are needed. The inner functions are annotated too, so mypy can check that their bodies keep the promise.

## Code

```python
from collections.abc import Callable


def apply_all(func: Callable[[int], int], numbers: list[int]) -> list[int]:
    return [func(n) for n in numbers]


def keep_if(test: Callable[[int], bool], numbers: list[int]) -> list[int]:
    return [n for n in numbers if test(n)]


def compose(first: Callable[[int], int], second: Callable[[int], int]) -> Callable[[int], int]:
    def both(x: int) -> int:
        return second(first(x))

    return both


def make_adder(n: int) -> Callable[[int], int]:
    def add(x: int) -> int:
        return x + n

    return add
```

## Complexity

`apply_all` and `keep_if`: O(n) calls of the given function. `compose` and `make_adder` return in O(1); the cost is paid when the returned function is called.

## Another way

`make_adder` can return a `lambda`: `return lambda x: x + n`. A lambda cannot carry its own hints, but mypy works the types out from the declared return type. A named inner function is easier to read and to annotate.
