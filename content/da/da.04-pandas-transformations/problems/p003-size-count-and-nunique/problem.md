# `size`, `count` and `nunique`

Chapter section 2.4. Three counts that look alike answer three different questions:

| Method | Counts | Missing values |
|---|---|---|
| `size()` | rows in the group | counts them |
| `count()` | non-missing values in a column | skips them |
| `nunique()` | different values in a column | skips them |

Write `customer_counts(lines)`. `lines` has one row per order line, with columns `customer_id`, `order_id`,
`product_id` and `coupon` (a coupon code, or missing when no coupon was used on that line). Some old lines have a
missing `product_id`.

Return one row per customer with these columns, in this order:

- `customer_id`
- `lines`: the number of lines of that customer (every row counts);
- `with_coupon`: the number of lines that have a coupon;
- `distinct_products`: how many **different** products the customer bought (a missing product is not a product).

Rows sorted by `customer_id`, index `0, 1, 2, ...`. Do not change `lines`.

## Example

```python
import pandas as pd

lines = pd.DataFrame({
    "customer_id": ["A", "A", "A", "B"],
    "order_id": [1, 1, 2, 3],
    "product_id": ["P1", "P2", "P1", "P3"],
    "coupon": ["SAVE10", "SAVE10", None, None],
})
print(customer_counts(lines))
```

```text
  customer_id  lines  with_coupon  distinct_products
0           A      3            2                  2
1           B      1            0                  1
```
