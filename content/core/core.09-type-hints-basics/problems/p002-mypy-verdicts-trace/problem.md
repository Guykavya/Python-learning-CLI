# Which lines does mypy flag?

Here is a file that you run through `python -m mypy`. Every line you must judge has a letter in a
comment at the end.

```python
def double(n: int) -> int:
    return n * 2


a = double(4)             # A
b = double("4")           # B
c: str = double(4)        # C
d: float = double(4)      # D
e = double(2.5)           # E
f = double(True)          # F
g: int = "7"              # G
h: str = str(double(1))   # H
```

mypy reads the hints and checks every line. For each letter, decide whether mypy reports an error
on that line (`error`) or accepts it (`ok`).

Write one line per letter, in order, in the form `A: ok` or `B: error`.

Write your answer in `answer.txt`.

**Remember**: an `int` is accepted where a `float` is expected, and a `bool` is accepted where an
`int` is expected. mypy does not run the code, so it only cares about types, not about what the
values would be.
