## Approach

`out[idx] += values` is "buffered": NumPy gathers `out[idx]` into a temporary, adds, and scatters the result back. Two sales of product 0 both read the old value 0, both compute 1, and both write 1: one sale is lost. `np.add.at` is the **unbuffered** version that applies every addition one after another, so duplicates accumulate. For pure counting, `np.bincount` is the purpose-built (and faster) tool; `minlength=n` makes sure products with no sales still get a 0 at the end.

## Code

```python
import numpy as np


def count_by_index(idx, n):
    return np.bincount(idx, minlength=n)


def add_amounts(totals, idx, amounts):
    out = totals.copy()
    np.add.at(out, idx, amounts)
    return out
```

## Complexity

O(len(idx) + n) for both. `np.add.at` is slower per element than `bincount` but still far faster than a Python loop.

## Another way

`np.bincount` also takes weights: `totals + np.bincount(idx, weights=amounts, minlength=len(totals))` adds the amounts in one fast call and returns a new array. This is the vectorised form of "group by product and sum", which pandas will give you in da.03 as `groupby(...).sum()`.
