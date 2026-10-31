# Trace: what does the checker infer for `T`?

A type checker fills in each `TypeVar` from the arguments of a call. Below is a file that you
run through `python -m mypy`. The four helper functions are generic.

```python
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def first(items: Sequence[T]) -> T:
    return items[0]


def pair(a: T, b: T) -> list[T]:
    return [a, b]


def wrap(x: T) -> list[T]:
    return [x]


def same(a: T, b: list[T]) -> T:
    return a


reveal_type(first([1, 2, 3]))        # A
reveal_type(first("hello"))          # B
reveal_type(wrap(2.5))               # C
reveal_type(pair("a", "b"))          # D
reveal_type(wrap(wrap(1)))           # E
reveal_type(first([[1], [2]]))       # F
x: str = first([1, 2])               # G
y: float = first([1, 2])             # H
z: int = same(1, [2])                # I
w: int = same(1, ["a"])              # J
reveal_type(first((1, 2, 3)))        # K
```

`reveal_type(expr)` makes mypy print the type it infers for `expr` (mypy prints it as a note, and
only the type matters here; write it the way mypy shows it, for example `int` or `list[str]`).
Lines `G` to `J` are assignments with a declared type: for them decide whether mypy reports an
error on that line (`error`) or accepts it (`ok`).

Write one line per letter, in order, in the form `A: int`, `C: list[float]` or `G: error`.

Write your answer in `answer.txt`.

**Remember**: mypy picks the one type for `T` that fits **all** the places `T` appears in the
call, then replaces `T` everywhere in the signature, including the return type.
