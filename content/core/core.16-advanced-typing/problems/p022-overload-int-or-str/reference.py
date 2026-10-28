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
