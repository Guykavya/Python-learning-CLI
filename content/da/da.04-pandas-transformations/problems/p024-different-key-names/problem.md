# Different key names

Chapter section 6.6. When the key has different names in the two tables, merge with `left_on=` and `right_on=`; the
result then has **both** key columns, so drop the one you do not need. When both tables have a non-key column with the
same name, pandas adds `_x` and `_y`. Choose your own `suffixes=` so that the names mean something.

Write `attach_store_names(orders, stores)`.

- `orders` has `order_id`, `customer_id`, `store_id` and `city` (the **customer's** city, attached earlier).
- `stores` comes from another system: `sid` (the store id, unique), `city` (the **store's** city) and `region`.
- Return every order, in the original order, index `0, 1, 2, ...`, with exactly these columns:
  `order_id`, `customer_id`, `store_id`, `city_customer`, `city_store`, `region`.
- An order whose store is not in `stores` is kept with missing `city_store` and `region`. The row count equals the
  number of orders.

Do not change the inputs.

## Example

```python
import pandas as pd

orders = pd.DataFrame({"order_id": [1, 2], "customer_id": ["C1", "C2"],
                       "store_id": ["S2", "S1"], "city": ["Pune", "Agra"]})
stores = pd.DataFrame({"sid": ["S1", "S2"], "city": ["Pune", "Delhi"], "region": ["west", "north"]})
print(attach_store_names(orders, stores))
```

```text
   order_id customer_id store_id city_customer city_store region
0         1          C1       S2          Pune      Delhi  north
1         2          C2       S1          Agra       Pune   west
```
