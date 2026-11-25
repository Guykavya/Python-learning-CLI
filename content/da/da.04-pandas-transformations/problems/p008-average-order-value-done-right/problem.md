# Average order value done right

Chapter section 3.5. **Average order value** (AOV) is the revenue divided by the number of **orders** (baskets).
Two easy-looking shortcuts give other numbers: the mean of the **line** revenues (a line is not an order), and the
mean of the **store** AOVs (a store with one order would weigh as much as a store with a thousand).

Write `average_order_value(lines)`. `lines` has one row per order line: `order_id`, `store_id`, `qty`,
`unit_price`; every order belongs to one store. Return a tuple `(overall, by_store)`:

- `overall`: total revenue (sum of `qty * unit_price`) divided by the number of different orders, as a plain `float`;
- `by_store`: one row per store with columns `store_id`, `revenue`, `orders` (different orders), `aov`
  (`revenue / orders`), sorted by `store_id`, index `0, 1, 2, ...`.

Do not change `lines`.

## Example

```python
import pandas as pd

lines = pd.DataFrame({
    "order_id": [1, 2, 3, 3],
    "store_id": ["S1", "S1", "S2", "S2"],
    "qty": [1, 1, 1, 1],
    "unit_price": [100.0, 100.0, 100.0, 300.0],
})
overall, by_store = average_order_value(lines)
print(overall)
print(by_store)
```

```text
200.0
  store_id  revenue  orders    aov
0       S1    200.0       2  100.0
1       S2    400.0       1  400.0
```

The shop took 600 in 3 orders: AOV 200. The mean of the two store AOVs is (100 + 400) / 2 = 250, and the mean line
revenue is 600 / 4 = 150. Neither is the AOV.
