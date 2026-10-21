## Approach

The greedy method: take as many of the largest note as fit, then repeat with what is left.
Working in integer paise makes every step exact.

## Code

```python
from decimal import Decimal

rest = int(Decimal(input()) * 100)
n500, rest = divmod(rest, 50000)
n100, rest = divmod(rest, 10000)
n50, rest = divmod(rest, 5000)
n10, rest = divmod(rest, 1000)
n5, rest = divmod(rest, 500)
n1, rest = divmod(rest, 100)
print("500:", n500)
print("100:", n100)
print("50:", n50)
print("10:", n10)
print("5:", n5)
print("1:", n1)
print("paise:", rest)
```

## Why rebinding `rest` works

Each `divmod` line reads the current `rest` on the right, then rebinds `rest` to the new remainder.
The right side is always evaluated before the names on the left are bound.

## Another way

`rest % 50000` at each step and `rest // 10000` from that, but `divmod` gives both in one call.
In core.04 a loop over the note values removes the repetition.
