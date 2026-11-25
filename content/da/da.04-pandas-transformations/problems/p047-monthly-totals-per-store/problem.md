# Monthly totals per store

Chapter section 9.7. `resample` works on one time series. With many stores in one table, `groupby` can split by store
**and** cut the dates into months in one call, with `pd.Grouper`.

Write `store_month(orders)`:

- `orders` has the columns `order_id`, `store_id`, `order_date` and `revenue` (in any order);
- return a frame with the columns `store_id`, `month` and `revenue`: one row per store and calendar month **in which
  that store has at least one order**, `month` being the last day of the month (a date, as `"ME"` labels it) and
  `revenue` the month's total;
- rows sorted by `store_id`, then `month`; fresh index; do not change the input.

The tests compare your answer with a loop over the orders on random data.

## Example

```python
import pandas as pd

orders = pd.DataFrame({"order_id": [1, 2, 3, 4],
                       "store_id": ["S1", "S2", "S1", "S1"],
                       "order_date": pd.to_datetime(["2025-01-05", "2025-01-09", "2025-01-31", "2025-03-02"]),
                       "revenue": [10.0, 3.0, 5.0, 20.0]})
out = store_month(orders)
print(out["store_id"].tolist(), out["month"].dt.strftime("%Y-%m-%d").tolist(), out["revenue"].tolist())
```
```text
['S1', 'S1', 'S2'] ['2025-01-31', '2025-03-31', '2025-01-31'] [15.0, 20.0, 3.0]
```

S1 has no order in February, so it has no February row.
