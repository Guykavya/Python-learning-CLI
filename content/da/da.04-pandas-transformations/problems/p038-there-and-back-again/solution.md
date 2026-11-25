## Approach

A wide table has a cell for **every** store and month, so absent pairs must become `NaN`, and a column with `NaN` is
`float64`. Going back, each `NaN` cell is a pair that was absent, so drop it; then no missing value is left and the
column can be cast back to `int64`. Sorting and a fresh index make the row order independent of how the tables were
built.

## Code

```python
import pandas as pd


def to_wide(long):
    wide = long.pivot(index="store_id", columns="month", values="sales").reset_index()
    wide.columns.name = None
    return wide


def to_long(wide):
    long = wide.melt(id_vars="store_id", var_name="month", value_name="sales")
    long = long.dropna(subset=["sales"])
    long = long.astype({"sales": "int64"})
    return long.sort_values(["store_id", "month"]).reset_index(drop=True)
```

## Complexity

O(n log n) each way, n = stores × months, for the sorts.

## Another way

Keep the gaps as a nullable integer: `long.astype({"sales": "Int64"})` before pivoting keeps whole numbers with `<NA>`
in the wide table. Then the wide table is not float, but every consumer must handle `Int64`. Also, a property test like
the one in `test_solution.py` (many random small tables, compare after a round trip) is the cheapest way to trust any
pair of inverse functions.
