## Approach

`melt` is the inverse of `pivot`: `store_id` stays, each month column becomes rows, its name goes into `month` and its
cell into `sales`. `melt` stacks column after column (all stores for the first column, then the next), so sort
afterwards. Text months in the form `"YYYY-MM"` sort in calendar order because the year comes first and the month has
two digits.

## Code

```python
import pandas as pd


def to_long(wide):
    long = wide.melt(id_vars="store_id", var_name="month", value_name="sales")
    return long.sort_values(["store_id", "month"]).reset_index(drop=True)
```

## Complexity

O(n log n) for the sort, where n = stores × months; the melt itself is linear.

## Another way

`wide.set_index("store_id").stack().rename("sales").reset_index()` (then rename the level column to `month`) is the
index flavour from section 8.5. In pandas 3 `stack` keeps missing cells too.
