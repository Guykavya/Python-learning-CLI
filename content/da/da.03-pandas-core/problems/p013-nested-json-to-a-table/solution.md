## Approach

`record_path="items"` turns each element of the `items` list into a row. `meta` names the order-level fields to repeat on every row; a nested field is a list of keys (`["customer", "name"]`) and arrives as the column `customer.name`. By default a missing meta key raises `KeyError`; `errors="ignore"` fills it with a missing value. Items lacking `qty` already give `NaN`. An order with an empty list contributes no rows. Finally rename, fix the `id` dtype (it arrives as `object`) and order the columns with `reindex(columns=...)`, which also creates a column that no record had (plain `[[...]]` would raise `KeyError`).

## Code

```python
import pandas as pd


def orders_from_json(records):
    flat = pd.json_normalize(
        records,
        record_path="items",
        meta=["id", ["customer", "name"]],
        errors="ignore",
    )
    flat = flat.rename(columns={"customer.name": "customer"})
    flat["id"] = flat["id"].astype("int64")
    return flat.reindex(columns=["id", "customer", "sku", "qty"])
```

## Complexity

O(total number of items).

## Another way

A plain double loop building a list of tuples, then `pd.DataFrame(rows, columns=[...])`, is just as correct and easy to read; `json_normalize` wins when the nesting is deeper or the keys are many.
