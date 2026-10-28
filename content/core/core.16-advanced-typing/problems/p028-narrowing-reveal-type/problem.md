# Trace: what does reveal_type show?

`reveal_type(expr)` makes mypy print the type it has worked out for `expr` at that line. Here is
a file with eleven of them (A to K). Each is inside a function whose parameter has a union type.
Narrowing (`is None`, `isinstance`, truthiness, assignments) changes the type from line to line.

```python
def f1(x: int | str | None) -> None:
    if x is None:
        return
    reveal_type(x)                      # A


def f2(x: int | str | None) -> None:
    if isinstance(x, str):
        reveal_type(x)                  # B
    else:
        reveal_type(x)                  # C


def f3(x: str | None) -> None:
    if x:
        reveal_type(x)                  # D
    y = x or "default"
    reveal_type(y)                      # E


def f4(x: int | str | list[int]) -> None:
    if isinstance(x, (int, str)):
        reveal_type(x)                  # F
    else:
        reveal_type(x)                  # G


def f5(items: list[str | None]) -> None:
    for item in items:
        if item is not None:
            reveal_type(item)           # H
    reveal_type(items)                  # I


def f6(x: int | str) -> None:
    y = x
    if isinstance(y, int):
        y = str(y)
    reveal_type(y)                      # J
    reveal_type(x)                      # K
```

For each letter, write the type mypy reveals, spelled as you would write it in a hint
(`int`, `str`, `int | str`, `list[int]`, `list[str | None]`, ...). Where a union is revealed, keep
the members in the order they appear in the function's parameter hint.

One line per letter, in order:

```text
A: int
B: str | None
```

(Those two lines are only the format, not the answers.)

Write your answer in `answer.txt`.

**Remember**: narrowing follows the code. After a `return`, the cases that returned are gone from
the rest of the function. `isinstance(x, (int, str))` removes every member that is not `int` or `str`.
A type checker does not look inside a list when you narrow the list itself.
