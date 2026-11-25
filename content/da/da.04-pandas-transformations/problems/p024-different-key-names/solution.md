## Approach

`left_on="store_id", right_on="sid"` matches the two differently named keys. Both key columns survive, so `sid` is
dropped (an order with an unknown store would have a missing `sid` anyway). Both tables have `city`, which is not a key,
so pandas suffixes it; `suffixes=("_customer", "_store")` gives names that say whose city it is. A left join with
`validate="m:1"` keeps exactly one row per order.

## Code

```python
import pandas as pd


def attach_store_names(orders, stores):
    out = orders.merge(stores, left_on="store_id", right_on="sid", how="left",
                       suffixes=("_customer", "_store"), validate="m:1")
    return out.drop(columns="sid")
```

## Complexity

O(n + s) for the hash join.

## Another way

Rename before merging, so both sides share the key and the clash disappears:
`stores.rename(columns={"sid": "store_id", "city": "city_store"})`, then `on="store_id"` and rename the order's `city`
to `city_customer`. More lines, but no suffixes to remember.
