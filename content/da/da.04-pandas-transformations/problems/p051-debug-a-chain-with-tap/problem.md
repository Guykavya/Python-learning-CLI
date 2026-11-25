# Debug a chain with `tap`

Chapter sections 11.3 and 11.4. A method chain hides its middle tables. A **tap** is a tiny step that records
something about the table and returns it unchanged, so you can see where rows appear or vanish.

Write two functions.

`tap(d, label, log)` appends the tuple `(label, d.shape)` to the list `log` and returns `d` itself.

`clean_items(items, log)` cleans order lines in **one chain** with `pipe(tap, ...)` after each step, using exactly these
steps and labels, in this order:

| step | then tap with label |
|---|---|
| (the raw table) | `"start"` |
| keep lines whose `qty` is present and greater than 0 | `"valid qty"` |
| drop rows that are exact duplicates of an earlier row | `"no duplicates"` |
| add `revenue = qty * unit_price` | `"with revenue"` |
| total revenue per order: columns `order_id`, `revenue`, sorted by `order_id` | `"per order"` |

`items` has the columns `order_id`, `product_id`, `qty` (a float, because some are missing) and `unit_price`. Return
the per-order table with a fresh index. After the call, `log` holds the five records. Do not change `items`.

## Example

```python
import pandas as pd

items = pd.DataFrame({"order_id": [1, 1, 2, 2], "product_id": ["P1", "P1", "P2", "P3"],
                      "qty": [2.0, 2.0, 0.0, 1.0], "unit_price": [10.0, 10.0, 5.0, 7.0]})
log = []
out = clean_items(items, log)
print(log)
print(out.values.tolist())
```
```text
[('start', (4, 4)), ('valid qty', (3, 4)), ('no duplicates', (2, 4)), ('with revenue', (2, 5)), ('per order', (2, 2))]
[[1.0, 20.0], [2.0, 7.0]]
```

(The order ids print as `1.0` because `values` puts the two columns into one float array.)
