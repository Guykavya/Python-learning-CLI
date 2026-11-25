## Approach

Every step returns a new table, so they chain. `loc[lambda d: ...]` filters the table **as it is at that step**,
`drop_duplicates()` compares whole rows, `assign` adds a column, `groupby(..., as_index=False)` keeps `order_id` as a
column (and sorts the keys). The taps record the shape after each step without changing anything, so the log reads
like a story: 8 rows, 5 valid, 4 unique, 3 orders.

## Code

```python
import pandas as pd


def tap(d, label, log):
    log.append((label, d.shape))
    return d


def clean_items(items, log):
    return (
        items
        .pipe(tap, "start", log)
        .loc[lambda d: d["qty"].notna() & (d["qty"] > 0)]
        .pipe(tap, "valid qty", log)
        .drop_duplicates()
        .pipe(tap, "no duplicates", log)
        .assign(revenue=lambda d: d["qty"] * d["unit_price"])
        .pipe(tap, "with revenue", log)
        .groupby("order_id", as_index=False)["revenue"].sum()
        .pipe(tap, "per order", log)
        .reset_index(drop=True)
    )
```

## Complexity

O(n log n) (the duplicate check and the groupby hash or sort the rows).

## Another way

`query("qty > 0")` also works for the filter: a missing `qty` compares as `False`, so it drops those rows too. Being
explicit with `notna()` says that the missing values are dropped on purpose. A tap can record more than the shape, for
example `d["revenue"].sum()` once that column exists, to watch money as well as rows.
