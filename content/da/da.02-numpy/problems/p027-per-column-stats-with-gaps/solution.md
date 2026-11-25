## Approach

Do what `np.nanmean` does, by hand, so you control the empty columns. Replace each `nan` with `0` **in a new array** (`np.where(valid, x, 0.0)`), so it adds nothing to the column sum, and count the valid entries with `valid.sum(axis=0)`. The mean is sum / count, but only where count > 0: `np.divide(..., where=has_data)` skips the other columns, and the `out` array, pre-filled with `nan`, keeps `nan` there. No division by zero happens, so no warning.

The variance works the same way: deviations from the column mean, zeroed where the value was missing, squared, summed, divided by the count. `x - mean` broadcasts the `(cols,)` mean over every row (Ch. 11). Subtracting `nan` from `nan` gives `nan` quietly: arithmetic on `nan` does not warn, only a division by zero or a reduction of an empty slice does.

## Code

```python
import numpy as np


def column_stats(x):
    x = np.asarray(x, dtype=float)
    valid = ~np.isnan(x)
    count = valid.sum(axis=0)
    has_data = count > 0
    total = np.where(valid, x, 0.0).sum(axis=0)
    mean = np.divide(total, count, out=np.full(x.shape[1], np.nan), where=has_data)
    dev = np.where(valid, x - mean, 0.0)
    var = np.divide((dev ** 2).sum(axis=0), count, out=np.full(x.shape[1], np.nan), where=has_data)
    return {"count": count, "mean": mean, "std": np.sqrt(var)}
```

## Complexity

O(rows × cols) time and a few temporary arrays of the table's size. No loop over columns.

## Another way

Call `np.nanmean` and `np.nanstd` only on the columns that have data, and fill the rest with `nan`:

```python
mean = np.full(cols, np.nan)
mean[has_data] = np.nanmean(x[:, has_data], axis=0)
```

Selecting the columns first means the `nan*` functions never see an empty column, so they never warn. Wrapping the call in `warnings.catch_warnings()` + `simplefilter("ignore")` would also silence it, but hiding a warning is the weaker habit: you no longer notice other problems.
