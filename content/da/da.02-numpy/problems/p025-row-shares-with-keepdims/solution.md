## Approach

`keepdims=True` keeps the row totals as a column, shape `(rows, 1)`, which broadcasts across each row (Ch. 10.3). For the zero rows, the division must not happen at all: `np.where(totals == 0, 0, x / totals)` gives the right numbers but still computes `x / totals` everywhere first, so it warns. The ufunc keyword `where=` skips the masked places, and `out=` (pre-filled with zeros) supplies their value (Ch. 10.6).

## Code

```python
import numpy as np


def row_shares(x):
    x = np.asarray(x, dtype=float)
    totals = x.sum(axis=1, keepdims=True)
    out = np.zeros(x.shape)
    np.divide(x, totals, out=out, where=totals != 0)
    return out
```

## Complexity

O(rows × cols): one pass for the totals, one for the division.

## Another way

Replace the zero totals before dividing: `safe = np.where(totals == 0, 1, totals)` and then `x / safe`. A zero row divided by 1 stays zero, and nothing is ever divided by 0. Silencing the warning with `np.errstate` and repairing `nan`s afterwards also works, but hides real problems elsewhere.
