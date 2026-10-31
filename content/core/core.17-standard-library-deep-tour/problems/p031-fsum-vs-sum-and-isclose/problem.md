# Trace: float sums, fsum and isclose

A `float` stores a number in binary with about 16 significant digits. `0.1` cannot be written
exactly in binary (just as 1/3 cannot be written exactly in decimal), so every `0.1` is really
`0.1000000000000000055511151231257827...`. Each `+` then rounds its result to the nearest float.

`math.fsum(values)` adds a whole list while keeping track of the lost low digits, and rounds only
**once**, at the end. `math.isclose(a, b, rel_tol=1e-09, abs_tol=0.0)` is `True` when
`abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)`.

The function `add_up` below adds with a plain loop, one rounding per `+`. (Since Python 3.12 the
built-in `sum()` of floats uses a cleverer method and gives better results than this loop, so
`sum()` is not used here: the answers would depend on your Python version.)

Predict **every line** this program prints:

```python
import math


def add_up(values):
    total = 0.0
    for v in values:
        total += v
    return total


tenths = [0.1] * 10
print("A", add_up(tenths))
print("B", math.fsum(tenths))
print("C", add_up(tenths) == 1.0)
print("D", math.isclose(add_up(tenths), 1.0))
print("E", 0.1 + 0.2)
print("F", math.fsum([0.1, 0.2]) == 0.3)
print("G", math.isclose(1e-12, 0.0))
print("H", math.isclose(1e-12, 0.0, abs_tol=1e-9))
big = [1e16, 1.0, -1e16]
print("I", add_up(big))
print("J", math.fsum(big))
print("K", math.isclose(100.0, 101.0, rel_tol=0.01))
print("L", round(2.675, 2))
print("M", math.floor(-0.5), math.ceil(-0.5), round(-0.5), round(1.5), round(2.5))
```

More facts you need:

- `print` shows the shortest decimal that turns back into the same float, so a float that is
  exactly `1.0` prints as `1.0`, and one just below it prints with many 9s.
- Near `1e16`, floats are 2 apart: `1e16 + 1.0` cannot be stored and rounds back to `1e16`.
- `2.675` is really stored as `2.67499999999999982236431605997495353221893310546875`.
- `round(x)` with no digits returns an `int` and rounds halves to the **even** neighbour.

Write your answer in `answer.txt`, one printed line per line.

**Example** (one line, given away):

```text
E 0.30000000000000004
```
