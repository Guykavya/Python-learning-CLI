# Trace: `Literal` verdicts

`Literal["r", "w"]` is a type with exactly two allowed values. A plain `str` is **not** accepted
where a `Literal` is expected, because the checker cannot know which string it is. Here is a file
that you run through `python -m mypy`:

```python
from typing import Final, Literal

Mode = Literal["r", "w"]


def open_file(name: str, mode: Mode) -> None:
    print(name, mode)


def helper(s: str) -> None:
    open_file("a", s)             # A


open_file("a", "r")               # B
open_file("a", "x")               # C
m = "w"
open_file("a", m)                 # D
n: Final = "w"
open_file("a", n)                 # E
k: Literal[1, 2, 3] = 2           # F
j: Literal[1, 2, 3] = 4           # G
v: Literal["a"] = "a"
s: str = v                        # H
t: Literal["a"] = s               # I
mode: Mode = "r"
open_file("a", mode)              # J
open_file("a", "R")               # K
```

For each letter, decide whether mypy reports an error **on that line** (`error`) or accepts it
(`ok`).

Write one line per letter, in order, in the form `A: ok` or `B: error`.

Write your answer in `answer.txt`.

**Remember**: a literal value like `"r"` written directly is accepted if it is one of the
allowed values. A *variable* is accepted only if its type is itself a Literal (or a `Final` whose
value the checker remembers). A `Literal` is a kind of `str` (or `int`...), but not the other way round.
