# Trace: what does mypy say about ParamSpec and overloads?

You run `python -m mypy` on this file. Decide, for every lettered line, what mypy says.

```python
import functools
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar, overload

P = ParamSpec("P")
R = TypeVar("R")


def logged(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper


def sloppy(func: Callable[..., Any]) -> Callable[..., Any]:
    return func


@logged
def add(a: int, b: int = 0) -> int:
    return a + b


@sloppy
def sub(a: int, b: int = 0) -> int:
    return a - b


@overload
def parse(text: str) -> int: ...
@overload
def parse(text: bytes) -> float: ...
def parse(text: str | bytes) -> int | float:
    return 0


a = add(1, 2)                  # A
b = add("1", 2)                # B
c = add(1, 2, 3)               # C
d = add(a=1, b=2)              # D
e = sub("x", "y")              # E
reveal_type(add(5))            # F
reveal_type(sub(5))            # G
reveal_type(parse("5"))        # H
reveal_type(parse(b"5"))       # I
j = parse(5)                   # J
```

For lines **A, B, C, D, E and J**, write `ok` if mypy accepts the line, or `error` if it reports an
error on it.

For lines **F, G, H and I**, `reveal_type(...)` makes mypy print the type of the expression.
Write that type the way you would write it in a hint, for example `int`, `str`, `Any`,
`int | None`, `list[str]`.

One line per letter, in order, like this:

```text
A: ok
B: error
F: int
```

Write your answer in `answer.txt`.

**Remember**: the decorators have their own hints. Ask what each decorated name is **after** the
decorator ran: what parameters does `add` still remember, and what does `sub` remember?
