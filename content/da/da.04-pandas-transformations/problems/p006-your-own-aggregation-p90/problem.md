# Your own aggregation: p90

Chapter section 3.3. Any function that turns a group's column into **one value** can be an aggregation. The shop
promises "90% of orders are delivered within N days", so the operations team wants the **90th percentile** (p90) of
the delivery time per region, next to the median.

Write `p90_delivery_days(orders)`. `orders` has columns `order_id`, `region` and `delivery_days` (a float; missing
for orders not delivered yet). Return one row per region with these columns, in this order:

- `region`
- `delivered`: the number of orders with a known `delivery_days`;
- `median_days`: the median of `delivery_days`;
- `p90_days`: the 90th percentile, as `Series.quantile(0.9)` computes it (linear interpolation).

Missing values are skipped. A region whose orders are all undelivered still gets a row: `delivered` 0 and missing
statistics. Rows sorted by `region`, index `0, 1, 2, ...`. Write `p90` as your own named function and use it in `agg`.

## Example

```python
import pandas as pd

orders = pd.DataFrame({
    "order_id": [1, 2, 3, 4, 5],
    "region": ["west", "west", "west", "west", "north"],
    "delivery_days": [2.0, 6.0, None, 3.0, 4.0],
})
print(p90_delivery_days(orders))
```

```text
  region  delivered  median_days  p90_days
0  north          1          4.0       4.0
1   west          3          3.0       5.4
```

For `west` the known values are 2, 3, 6. The 90th percentile sits 0.9 of the way along the sorted list (position
0.9 × 2 = 1.8), so it is 3 + 0.8 × (6 − 3) = 5.4.
