# Rows, values, distinct values

Chapter section 5.1. "Count" is three operations: how many rows, how many rows have a value, how many different values.
Each one answers a different question about the same table.

`payments` has the columns `payment_id`, `customer_id` and `method` (`card`, `upi`, ...; **missing** when nobody recorded it).
Write `three_counts(payments)` returning a dict with plain `int`s:

- `"rows"`: the number of payments;
- `"with_method"`: the number of payments that have a method recorded;
- `"distinct_customers"`: the number of different customers who paid (missing customer ids are not customers).

Never change the table.

## Example

```python
import pandas as pd
from solution import three_counts

pay = pd.DataFrame({"customer_id": [1, 1, 2], "method": ["card", None, "upi"]})
print(three_counts(pay))
```

prints

```text
{'rows': 3, 'with_method': 2, 'distinct_customers': 2}
```

Three payments, two of them with a method, from two customers (customer 1 paid twice).
