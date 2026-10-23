# int, bool, float and invariance: which lines fail?

mypy checks each annotated line below. Decide for each letter whether it reports an error
(`error`) or accepts the line (`ok`).

```python
nums: list[int] = [1, 2]

a: float = 3                    # A
b: int = 3.0                    # B
c: int = True                   # C
d: bool = 1                     # D
e: float = False                # E
f: list[float] = [1, 2]         # F
g: list[float] = nums           # G
h: tuple[float, ...] = (1, 2)   # H
i: tuple[int, ...] = (1, 2.5)   # I
j: dict[str, float] = {"a": 1}  # J
k: dict[str, int] = {"a": 1.5}  # K
```

Write one line per letter, in order, in the form `A: ok` or `B: error`.

Write your answer in `answer.txt`.

Reminders: an `int` is accepted where a `float` is expected; a `bool` is accepted where an `int`
is expected; a `list` is **invariant** (a `list[int]` is not a `list[float]`). A list *literal*
such as `[1, 2]` takes its type from the place where it is used.
