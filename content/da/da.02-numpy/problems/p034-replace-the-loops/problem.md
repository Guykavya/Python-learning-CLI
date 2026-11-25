# Replace the loops

Chapter section 12.1 (the recipe), 12.2 and 11.6. This is the module's learning outcome "replace a Python loop with a vectorised NumPy expression". Here are three working loop functions:

```python
import numpy as np

def tax_loop(incomes):
    out = []
    for v in incomes:
        if v <= 25_000:
            out.append(0.0)
        elif v <= 75_000:
            out.append((v - 25_000) * 0.10)
        else:
            out.append(5_000 + (v - 75_000) * 0.30)
    return np.array(out, dtype=float)


def change_loop(prices, limit):
    out = []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]
        if change > limit:
            change = limit
        elif change < -limit:
            change = -limit
        out.append(change)
    return np.array(out, dtype=float)


def nearest_loop(values, centres):
    out = []
    for v in values:
        best = 0
        for j in range(1, len(centres)):
            if abs(v - centres[j]) < abs(v - centres[best]):
                best = j
        out.append(best)
    return np.array(out, dtype=np.int64)
```

Write `tax_vec(incomes)`, `change_vec(prices, limit)` and `nearest_vec(values, centres)` that return **the same results** without a Python loop over the data:

- `tax_vec`: income tax with three bands (0 up to 25,000; 10% of the part between 25,000 and 75,000; above that 5,000 plus 30% of the part over 75,000). `float64` array, same length as `incomes`.
- `change_vec`: the change from each day to the next, clipped to `[-limit, limit]`. `float64` array, one element shorter than `prices` (empty for 0 or 1 prices).
- `nearest_vec`: for every value, the **index** of the closest centre; on a tie the **lower** index wins (as in the loop, which only moves on a strictly smaller distance). Integer array, same length as `values`.

Inputs may be lists or arrays of numbers. Do not change them.

The test checks your results against the loops on random data, then times each function on **1,000,000** values against the loop on the same machine (the loop runs on 100,000 values and its time is multiplied by 10): your version must be at least 5 times faster. A vectorised version is typically 20 to 50 times faster.

## Example

```python
tax_vec([10_000, 25_000, 50_000, 75_000, 100_000])
# array([    0.,     0.,  2500.,  5000., 12500.])
change_vec([100, 103, 109, 101, 100], limit=5)
# array([ 3.,  5., -5., -1.])
nearest_vec([1.0, 4.9, 5.0, 12.0], [0.0, 10.0, 5.0])
# array([0, 2, 2, 1])
```
