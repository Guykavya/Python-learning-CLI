# Aggregate a computed value

Chapter section 3.4. You cannot aggregate "revenue after discount" until that column exists. Compute it **per line
first**, then group. Doing the arithmetic on group totals gives a different, wrong number.

Write `net_revenue_by_category(lines, products)`.

- `lines` has one row per order line: `order_id`, `product_id`, `qty`, `unit_price` and `discount` (a fraction:
  `0.1` means 10% off that line). The net revenue of a line is `qty * unit_price * (1 - discount)`.
- `products` is the chapter's product table: `product_id` (unique), `category`, `list_price`. Every product in
  `lines` is in `products`.
- Return one row per category **that has at least one line**, with columns `category` and `net_revenue`, sorted by
  `category`, index `0, 1, 2, ...`.
- The category totals must add up to the net revenue of all lines (the merge must not add or lose lines). Do not
  change the inputs.

## Example

```python
import pandas as pd

products = pd.DataFrame({"product_id": ["P1", "P2", "P3"],
                         "category": ["grocery", "home", "toys"],
                         "list_price": [10.0, 100.0, 30.0]})
lines = pd.DataFrame({"order_id": [1, 1, 2],
                      "product_id": ["P1", "P2", "P1"],
                      "qty": [2, 1, 1],
                      "unit_price": [10.0, 100.0, 10.0],
                      "discount": [0.0, 0.25, 0.5]})
print(net_revenue_by_category(lines, products))
```

```text
  category  net_revenue
0  grocery         25.0
1     home         75.0
```

Grocery: 2 × 10 × 1 + 1 × 10 × 0.5 = 25. `toys` sold nothing, so it has no row.
