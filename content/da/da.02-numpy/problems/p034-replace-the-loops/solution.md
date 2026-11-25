## Approach

Follow the recipe (Ch. 12.1): say what one pass computes, replace the loop variable by the whole array, `if`/`else` by a mask, "previous element" by a shift.

- **Tax.** Three bands = two nested `np.where`: the inner one picks between the middle and top band, the outer one zeroes the bottom band. Both branches are computed for every element and `where` picks; that is fine because both are cheap and valid everywhere. `np.select([x <= 25_000, x <= 75_000], [0.0, (x - 25_000) * 0.10], default=5_000 + (x - 75_000) * 0.30)` is the same, and reads better with more bands.
- **Change.** `prices[i] - prices[i - 1]` for every `i` is `np.diff(prices)`; the two `if`s that cap it are `np.clip`.
- **Nearest.** The inner loop compares one value with every centre; broadcasting a column of values `(n, 1)` against a row of centres `(1, k)` builds all distances `(n, k)` at once, and `argmin(axis=1)` picks the closest centre per row. `argmin` returns the first minimum, which is exactly the loop's "move only on strictly smaller" rule.

## Code

```python
import numpy as np


def tax_vec(incomes):
    x = np.asarray(incomes, dtype=float)
    return np.where(x <= 25_000, 0.0,
                    np.where(x <= 75_000, (x - 25_000) * 0.10, 5_000 + (x - 75_000) * 0.30))


def change_vec(prices, limit):
    p = np.asarray(prices, dtype=float)
    return np.clip(np.diff(p), -limit, limit)


def nearest_vec(values, centres):
    v = np.asarray(values, dtype=float)
    c = np.asarray(centres, dtype=float)
    return np.abs(v[:, None] - c[None, :]).argmin(axis=1)
```

## Complexity

Same O(n) (and O(n × k) for the nearest centre) as the loops, but the work happens in C: in the timing test the vectorised versions were about 20 to 50 times faster than the loops (measured in an earlier test run; your machine will differ). The nearest-centre table costs n × k floats of memory: for a million values and 5 centres, 40 MB.

## Another way

For the nearest centre with **sorted** centres you can avoid the `(n, k)` table: `np.searchsorted(centres, values)` finds the neighbour on the right, and one comparison with the neighbour on the left decides. That is O(n log k) time and O(n) memory, useful when `k` is large. The tax can also be written without `where`: `0.10 * np.clip(x - 25_000, 0, 50_000) + 0.30 * np.clip(x - 75_000, 0, None)` sums the tax of each band.
