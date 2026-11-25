# Customers who bought X (no duplicates)

Chapter section 6.5. A **semi-join** keeps the rows of one table that **do** have a match in another, each **once**,
without bringing the other table's columns along. A plain `merge` is the wrong tool: a customer who bought the
product three times would appear three times.

Write `bought_product(customers, lines, product_id)`.

- `customers` has `customer_id` (unique), `city`, `segment`.
- `lines` has one row per order line: `order_id`, `customer_id`, `product_id`, `qty`.
- Return the customers who bought `product_id` at least once: only the customer columns, each customer once, in the
  original customer order, index `0, 1, 2, ...`. If nobody bought it, return an empty frame with the same columns.

Do not change the inputs.

## Example

```python
import pandas as pd

customers = pd.DataFrame({"customer_id": ["C1", "C2", "C3"], "city": ["Pune", "Delhi", "Agra"],
                          "segment": ["retail", "retail", "premium"]})
lines = pd.DataFrame({"order_id": [1, 2, 3, 4], "customer_id": ["C3", "C3", "C1", "C3"],
                      "product_id": ["P7", "P7", "P2", "P7"], "qty": [1, 2, 1, 1]})
print(bought_product(customers, lines, "P7"))
```

```text
  customer_id  city  segment
0          C3  Agra  premium
```
