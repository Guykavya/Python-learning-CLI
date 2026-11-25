## Approach

One dimension per thing you want to slice by. The surrogate key is a small integer, independent of the names, so a name can change later without breaking the fact table. A many-to-one merge with `validate="m:1"` guarantees that the fact keeps one row per line.

## Code

```python
import pandas as pd


def _dim(flat, natural, attrs, key):
    d = flat[[natural] + attrs].drop_duplicates()
    if d[natural].duplicated().any():
        raise ValueError(f"conflicting attributes for {natural} {d.loc[d[natural].duplicated(), natural].iloc[0]}")
    d = d.sort_values(natural).reset_index(drop=True)
    d.insert(0, key, range(1, len(d) + 1))
    return d


def build_star(flat):
    dims = {"DimProduct": _dim(flat, "product", ["category"], "ProductKey"),
            "DimCustomer": _dim(flat, "customer", ["segment", "city"], "CustomerKey"),
            "DimStore": _dim(flat, "store", [], "StoreKey")}
    fact = flat[["order_id", "line_no", "order_date", "product", "customer", "store", "quantity", "unit_price", "discount"]]
    for dim, natural, key in (("DimProduct", "product", "ProductKey"), ("DimCustomer", "customer", "CustomerKey"), ("DimStore", "store", "StoreKey")):
        fact = fact.merge(dims[dim][[natural, key]], on=natural, how="left", validate="m:1")
    fact = fact[["order_id", "line_no", "order_date", "ProductKey", "CustomerKey", "StoreKey", "quantity", "unit_price", "discount"]]
    return fact.reset_index(drop=True), dims
```

## Complexity

O(n log n).

## Another way

`pd.factorize(sorted values)` or `pd.Categorical(...).codes + 1` also assign integer keys; the explicit merge is easier to check and keeps unmatched keys visible.
