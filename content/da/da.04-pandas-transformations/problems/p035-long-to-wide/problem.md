# Long to wide

Chapter sections 8.1 and 8.2. The table `monthly` is **long**: one row per store and month, with the columns
`store_id`, `month` (text such as `"2025-01"`) and `sales`. The manager wants it **wide**: one row per store, one column
per month.

Write `to_wide(monthly)`:

- the result has a first column `store_id`, then one column per month, months in sorted order (the text `"YYYY-MM"`
  sorts in calendar order);
- one row per store, stores sorted, fresh index `0, 1, ...`, and **no leftover name** on the column labels
  (`out.columns.name` is `None`);
- a store and month pair that is not in the long table becomes `NaN` (not 0: we do not know it was zero);
- `pivot` does no arithmetic, so if a (store, month) pair appears **more than once**, raise `ValueError` with a message
  that names at least one repeated pair and says to use `pivot_table` with an aggregation instead.

Do not change the input.

## Example

```python
import pandas as pd

monthly = pd.DataFrame({"store_id": ["S2", "S1", "S1", "S2"],
                        "month": ["2025-02", "2025-01", "2025-02", "2025-01"],
                        "sales": [30, 10, 15, 25]})
out = to_wide(monthly)
print(list(out.columns), out.columns.name)
print(out.values.tolist())
```
```text
['store_id', '2025-01', '2025-02'] None
[['S1', 10, 15], ['S2', 25, 30]]
```
