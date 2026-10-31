# Trace: Any versus object

`Any` and `object` both mean "could be anything", but a type checker treats them in opposite ways.
Here is a file you run through `python -m mypy`:

```python
from typing import Any


def show_any(x: Any) -> str:
    return x.upper()                    # A


def show_obj(x: object) -> str:
    return x.upper()                    # B


def length(x: object) -> int:
    if isinstance(x, str):
        return len(x)                   # C
    return 0


def take_int(n: int) -> int:
    return n


a: Any = "hello"
o: object = "hello"
n1 = take_int(a)                        # D
n2 = take_int(o)                        # E
s1: str = a                             # F
s2: str = o                             # G
o = 42                                  # H
a = 42                                  # I
reveal_type(a.whatever)                 # J
reveal_type(len(a))                     # K
print(show_any(123), show_obj(123))     # L
```

For the lines marked **A, B, C, D, E, F, G, H, I and L**, write `ok` if mypy accepts the line, or
`error` if it reports an error on it.

For **J** and **K**, `reveal_type(...)` makes mypy print the type of the expression. Write that
type the way you would write it in a hint (`int`, `str`, `Any`, ...).

One line per letter, in the order A, B, C, D, E, F, G, H, I, J, K, L:

```text
A: ok
B: error
J: Any
```

(Those lines only show the format.)

Write your answer in `answer.txt`.

**Remember**: mypy does not run the program. It only compares types. Think about what each
declared type promises, and what mypy is allowed to assume about it.
