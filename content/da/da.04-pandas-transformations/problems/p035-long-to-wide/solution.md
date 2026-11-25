## Approach

Check the one condition `pivot` relies on (each pair once) and fail with a helpful message. Then `pivot` puts
`store_id` values on the rows, `month` values on the columns and `sales` in the cells, sorting both. `reset_index`
turns the stores back into a column, and clearing `columns.name` removes the leftover label `month`.

## Code

```python
import pandas as pd


def to_wide(monthly):
    keys = ["store_id", "month"]
    dup = monthly[monthly.duplicated(subset=keys, keep=False)]
    if len(dup):
        pairs = sorted(set(zip(dup["store_id"], dup["month"])))
        raise ValueError(f"(store_id, month) pairs repeat, e.g. {pairs[0]}: "
                         "pivot cannot add them up; use pivot_table with aggfunc='sum'")
    wide = monthly.pivot(index="store_id", columns="month", values="sales").reset_index()
    wide.columns.name = None
    return wide
```

## Complexity

O(n log n) for sorting the row and column labels; the cells are filled in one pass.

## Another way

`monthly.set_index(["store_id", "month"])["sales"].unstack("month")` is the same operation through the index (section
8.5); it also raises on repeated pairs. When repeats are real (two rows for the same month), `pivot_table(...,
aggfunc="sum")` is the right tool.
