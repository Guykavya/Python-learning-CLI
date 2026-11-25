# Join on two columns

Chapter sections 6.8 and 6.10. A daily target belongs to **a store on a date**: the key is the pair
`(store_id, date)`. Joining on `store_id` alone matches every sales day with every target day of that store: a
many-to-many fan-out.

Write `daily_targets(sales, targets)`.

- `sales`: one row per store and day: `store_id`, `date` (datetime), `revenue`.
- `targets`: at most one row per store and day: `store_id`, `date`, `target`. Some days have no target; some targets
  are for days with no sales.
- Return every sales row, in the original order, index `0, 1, 2, ...`, with columns `store_id`, `date`, `revenue`,
  `target` (missing when there is no target for that store and day) and `hit` (`True` when `revenue >= target`,
  `False` otherwise, including when there is no target). The row count equals the number of sales rows.

Do not change the inputs.

## Example

```python
import pandas as pd

d = pd.to_datetime(["2025-01-01", "2025-01-02"])
sales = pd.DataFrame({"store_id": ["S1", "S1", "S2"], "date": [d[0], d[1], d[0]], "revenue": [100.0, 80.0, 50.0]})
targets = pd.DataFrame({"store_id": ["S1", "S1"], "date": [d[0], d[1]], "target": [90.0, 90.0]})
print(daily_targets(sales, targets))
```

```text
  store_id       date  revenue  target    hit
0       S1 2025-01-01    100.0    90.0   True
1       S1 2025-01-02     80.0    90.0  False
2       S2 2025-01-01     50.0     NaN  False
```
