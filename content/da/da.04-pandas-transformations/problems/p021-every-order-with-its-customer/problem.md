# Every order, with its customer

Chapter sections 6.2 and 6.3. The orders table is the main table: no order may be lost or duplicated when you attach
customer details. That is a **left** join with orders on the left. The golden rule: the row count after the merge
equals the number of orders. Orders whose `customer_id` is not in `customers` (orphan keys) are kept, with missing
customer details, and **counted** so that someone can fix the data.

Write `orders_with_customers(orders, customers)`.

- `orders` has `order_id`, `customer_id`, `store_id`.
- `customers` has `customer_id` (unique), `city`, `segment`.
- Return a tuple `(table, unknown)`: `table` has every order, in the original order, index `0, 1, 2, ...`, with the
  columns of `orders` followed by `city` and `segment`; `unknown` is the number of orders (a plain `int`) whose
  customer is not in `customers`.

Do not change the inputs.

## Example

```python
import pandas as pd

orders = pd.DataFrame({"order_id": [1, 2, 3], "customer_id": ["C1", "C9", "C1"], "store_id": ["S1", "S2", "S1"]})
customers = pd.DataFrame({"customer_id": ["C1", "C2"], "city": ["Pune", "Agra"], "segment": ["retail", "premium"]})
table, unknown = orders_with_customers(orders, customers)
print(table)
print(unknown)
```

```text
   order_id customer_id store_id  city segment
0         1          C1       S1  Pune  retail
1         2          C9       S2   NaN     NaN
2         3          C1       S1  Pune  retail
1
```
