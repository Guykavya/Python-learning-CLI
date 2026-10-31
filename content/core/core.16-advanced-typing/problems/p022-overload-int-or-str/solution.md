## Approach

Each `@overload` is a promise to the checker: "if you call me with these argument types, you get
this result type". The checker tries them in order and takes the first that fits. The undecorated
last definition holds the real code; its own hints must be wide enough to accept every overload.
Python keeps only that last function at run time, but `typing.get_overloads` can still list the
signatures (that is how the tests read them).

For `to_number`, the flag's **value** decides the result, so we use `Literal[True]` and
`Literal[False]`. The default `False` sits on the second overload only: a call with no flag has to
match exactly one signature, and it is the `int` one.

## Code

```python
from typing import Literal, overload


@overload
def double(x: int) -> int: ...
@overload
def double(x: str) -> str: ...
def double(x: int | str) -> int | str:
    if isinstance(x, (int, str)):
        return x * 2
    raise TypeError(f"cannot double {type(x).__name__}")


@overload
def to_number(text: str, as_float: Literal[True]) -> float: ...
@overload
def to_number(text: str, as_float: Literal[False] = False) -> int: ...
def to_number(text: str, as_float: bool = False) -> int | float:
    if as_float:
        return float(text)
    return int(text)
```

## Complexity

O(1) for `double` on an `int`, O(n) for a `str` of length n. `to_number` is O(len(text)).

## Another way

A `TypeVar` with constraints, `T = TypeVar("T", int, str)`, can write `double` in one signature:
`def double(x: T) -> T`. Use overloads when the result is not the same type as the argument
(as in `to_number`) or when the parameters themselves change between the signatures.
