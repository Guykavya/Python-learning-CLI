## Approach

A 1-D boolean mask with one entry per row, used as the first index, selects whole rows: `table[keep]` has shape `(number of True, ncols)`, also when that number is 0. Each condition is a comparison in its own brackets, combined with `&` (and), `|` (or) and `~` (not). Comparisons with `nan` are `False`, so a missing value is never "between".

## Code

```python
import numpy as np


def select_rows(table, col, lo, hi, exclude=None):
    values = table[:, col]
    keep = (values >= lo) & (values <= hi)
    if exclude is not None:
        keep = keep & ~(table[:, exclude] != 0)
    return table[keep]


def outside_rows(table, col, lo, hi):
    values = table[:, col]
    return table[(values < lo) | (values > hi)]
```

## Complexity

O(rows) for the masks plus a copy of the selected rows (a mask gives a copy, so the input is safe).

## Another way

`outside_rows` is exactly the rows `select_rows` does not keep: `table[~((values >= lo) & (values <= hi))]`. That is true for numbers, but not with `nan`: a `nan` row is neither between nor outside with `<`/`>`, while `~(between)` counts it as outside. Decide what missing values should do and write it down. `np.logical_and` / `np.logical_or` / `np.logical_not` are the word versions of `&`, `|`, `~`.
