## Approach

`wide_to_long` finds every column that starts with a stub and the separator, takes the rest of the name as the value
of `j`, and gives one row per (i, j) pair with one column per stub. The years are digits, so `j` becomes an integer.
The result is indexed by `(store_id, year)`; `reset_index` turns them into columns, then sort and renumber.

## Code

```python
import pandas as pd


def yearly_long(df):
    out = pd.wide_to_long(df, stubnames=["sales", "units"], i="store_id", j="year", sep="_").reset_index()
    out = out[["store_id", "year", "sales", "units"]]
    return out.sort_values(["store_id", "year"]).reset_index(drop=True)
```

## Complexity

O(stores × columns), plus O(n log n) for the sort.

## Another way

With tools you already know: `melt(id_vars="store_id")`, split the old column name with
`.str.split("_", expand=True)` into `measure` and `year`, convert `year` with `astype(int)`, and `pivot` back with
`index=["store_id", "year"], columns="measure", values="value"`. It is longer but shows what `wide_to_long` does.
