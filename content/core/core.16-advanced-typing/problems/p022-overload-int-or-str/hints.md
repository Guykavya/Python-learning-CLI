## Hint 1

How many different return types does `double` have? What is the *link* between the argument type and the result type? What does a signature look like when it has no body, only `...`?

## Hint 2

`from typing import overload`. Put `@overload` above each signature-only definition, then write the real function last, without a decorator. The real function's hints are the wide union (`int | str`) and it does the work with `isinstance`. For `to_number`, the flag has the type `Literal[True]` in one overload and `Literal[False] = False` in the other.

## Hint 3

```
@overload
def double(x: int) -> int: ...
@overload
def double(x: str) -> str: ...
def double(x: int | str) -> int | str:
    if isinstance(x, (int, str)): return x * 2
    raise TypeError

@overload
def to_number(text: str, as_float: Literal[True]) -> float: ...
@overload
def to_number(text: str, as_float: Literal[False] = False) -> int: ...
def to_number(text: str, as_float: bool = False) -> int | float: ...
```
