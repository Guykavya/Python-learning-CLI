# Named aggregation

Chapter section 3.2. Named aggregation gives several statistics from different columns in one step, with output
column names **you** choose: `agg(new_name=("column", "function"), ...)`.

Write `store_summary(lines)`. `lines` has one row per order line with columns `order_id`, `store_id`, `product_id`,
`qty` and `unit_price`. Return one row per store with exactly these columns, in this order:

- `store_id`
- `orders`: the number of **different** orders of the store (an order with three lines is one order);
- `revenue`: the sum of `qty * unit_price` over the store's lines;
- `units`: the total `qty`.

Rows sorted by `store_id`, index `0, 1, 2, ...`. Do not change `lines` (no new column in the caller's frame).

## Example

```python
import pandas as pd

lines = pd.DataFrame({
    "order_id": [1, 1, 2, 3],
    "store_id": ["S1", "S1", "S1", "S2"],
    "product_id": ["P1", "P2", "P1", "P3"],
    "qty": [2, 1, 1, 3],
    "unit_price": [10.0, 5.5, 10.0, 4.0],
})
print(store_summary(lines))
```

```text
  store_id  orders  revenue  units
0       S1       2     35.5      4
1       S2       1     12.0      3
```
