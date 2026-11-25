# Customers who never ordered

Chapter section 6.5. An **anti-join** keeps the rows of one table that have **no match** in another. pandas has no
keyword for it; `~isin(...)` or a left merge with `indicator=True` builds it.

Write `never_ordered(customers, orders)`.

- `customers` has `customer_id` (unique), `city`, `segment`.
- `orders` has `order_id`, `customer_id`, `store_id`. Some orders belong to customers that do not exist (orphans);
  they do not matter here.
- Return the customers with **no** order: only the customer columns, in the original customer order, index
  `0, 1, 2, ...`. If everybody ordered, return an empty frame with the same columns.

Do not change the inputs.

## Example

```python
import pandas as pd

customers = pd.DataFrame({"customer_id": ["C1", "C2", "C3"], "city": ["Pune", "Delhi", "Agra"],
                          "segment": ["retail", "retail", "premium"]})
orders = pd.DataFrame({"order_id": [1, 2, 3], "customer_id": ["C1", "C1", "C9"], "store_id": ["S1", "S2", "S1"]})
print(never_ordered(customers, orders))
```

```text
  customer_id   city  segment
0          C2  Delhi   retail
1          C3   Agra  premium
```
