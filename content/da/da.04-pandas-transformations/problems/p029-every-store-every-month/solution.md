## Approach

The rows of the answer are decided by the **dimensions** (stores × months), not by the facts (sales). A cross join builds
exactly `len(stores) * len(months)` rows. A left join from that grid attaches the sales on the pair of keys; cells
without a sale get `NaN`, which `fillna(0.0)` turns into "sold nothing". Sales outside the grid (unknown store, month
not asked for) have no grid cell and drop out. `validate="1:1"` confirms one sale per cell, so the count cannot grow.

## Code

```python
import pandas as pd


def full_grid(sales, stores, months):
    grid = stores[["store_id"]].merge(pd.DataFrame({"month": months}), how="cross")
    out = grid.merge(sales[["store_id", "month", "revenue"]], on=["store_id", "month"], how="left", validate="1:1")
    out["revenue"] = out["revenue"].fillna(0.0)
    return out.sort_values(["store_id", "month"], ignore_index=True)
```

## Complexity

O(S · M) rows in the grid, plus O(n) for the hash join of n sales and the sort of S · M rows.

## Another way

`pd.MultiIndex.from_product([stores["store_id"], months], names=["store_id", "month"])` builds the same grid as an
index; then `sales.set_index(["store_id", "month"])["revenue"].reindex(grid, fill_value=0.0).reset_index()`.
`reindex` returns to this idea for dates in Ch. 9.2.
