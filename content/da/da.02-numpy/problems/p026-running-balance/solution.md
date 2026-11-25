## Approach

The balance after transaction `i` is the opening balance plus the sum of the first `i + 1` transactions: that is exactly a running total, `np.cumsum`. Adding the scalar `opening` broadcasts it to every element. Converting with `np.asarray(txns, dtype=float)` gives `float64` even for integer input and makes an empty list a proper empty float array.

For the first overdraft, compare once (`balances < 0`) to get a mask. `np.argmax` on a boolean array returns the first position of the maximum, i.e. the first `True` (Ch. 10.5: ties go to the first). It returns `0` when everything is `False`, so check `.any()` first.

## Code

```python
import numpy as np


def running_balance(opening, txns):
    txns = np.asarray(txns, dtype=float)
    return opening + np.cumsum(txns)


def first_overdraft_day(opening, txns):
    below = running_balance(opening, txns) < 0
    if not below.any():
        return -1
    return int(np.argmax(below))
```

## Complexity

O(n) time for both, and one new array of n floats (plus the mask). No Python loop: `cumsum` runs in C.

## Another way

`np.flatnonzero(below)` lists all overdraft positions; its first element (if the list is not empty) is the answer. It builds a longer array than needed, but reads naturally: `days = np.flatnonzero(below); return int(days[0]) if days.size else -1`.
