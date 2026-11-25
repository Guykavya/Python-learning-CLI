# Revenue by one key or several

Chapter sections 2.1 and 2.2. A `groupby` with one key gives an index of keys; with a list of keys it gives a
**MultiIndex**. For a report you usually want the keys back as ordinary columns, so that the next step can say
`result["store_id"]`.

Write `revenue_by(lines, keys)`:

- `lines` is the order-line table of Ch. 2.2: one row per product line, with columns `order_id`, `product_id`,
  `store_id`, `channel` and `revenue` (already computed as `qty * unit_price`).
- `keys` is **one column name** (a string) **or a list** of column names.
- Return a new frame with one row per key (or key combination) and the columns: the key columns, then `revenue`
  (the sum). Rows sorted by the keys; the index is `0, 1, 2, ...` (a plain `RangeIndex`, no MultiIndex).
- Do not change `lines`.

## Example

```python
import pandas as pd

lines = pd.DataFrame({
    "order_id": [1, 1, 2, 3],
    "product_id": ["P1", "P2", "P1", "P3"],
    "store_id": ["S2", "S2", "S1", "S2"],
    "channel": ["store", "store", "online", "online"],
    "revenue": [10.0, 5.0, 20.0, 7.5],
})
print(revenue_by(lines, "store_id"))
print(revenue_by(lines, ["store_id", "channel"]))
```

```text
  store_id  revenue
0       S1     20.0
1       S2     22.5
  store_id channel  revenue
0       S1  online     20.0
1       S2  online      7.5
2       S2   store     15.0
```
