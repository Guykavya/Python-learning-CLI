# Average price, weighted

Chapter section 16.2. A table `df` has `order_id`, `qty` and `unit_price`. Write `summary_numbers(df)` that returns a
dict with four numbers:

| key | meaning |
|---|---|
| `"orders"` | the number of rows (an `int`) |
| `"units"` | the total quantity (an `int` when the quantities are whole numbers) |
| `"revenue"` | the sum of `qty * unit_price` (a `float`) |
| `"avg_price"` | the **weighted** average price: `revenue / units`, i.e. each price counts as often as units were sold (a `float`) |

For an empty table `orders` and `units` are `0`, `revenue` is `0.0` and `avg_price` is `None` (nothing was sold). The
input is not changed, and no loop is needed.

Careful: the plain `df["unit_price"].mean()` is **not** the answer. It counts a price used for 1 unit as much as a
price used for 1,000 units.

## Example

```python
import pandas as pd

from solution import summary_numbers

df = pd.DataFrame({"order_id": [1, 2, 3], "qty": [1, 1, 10], "unit_price": [100.0, 100.0, 10.0]})
print(summary_numbers(df))
print(df["unit_price"].mean())
```

```text
{'orders': 3, 'units': 12, 'revenue': 300.0, 'avg_price': 25.0}
70.0
```
