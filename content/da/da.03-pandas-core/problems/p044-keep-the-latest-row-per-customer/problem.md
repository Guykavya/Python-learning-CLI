# Keep the latest row per customer

Chapter section 14.4. A table `df` has one row per event: `row_id` (unique number), `customer` (text), `ts` (datetime)
and `amount`. Write `latest_per_customer(df)` that returns a pair `(latest, removed)`:

- `latest`: one row per customer, the **most recent** event by `ts`. If two events of a customer have the **same**
  `ts`, the one with the larger `row_id` wins. The rows are ordered by `customer` (A to Z) and the index is reset
  to `0, 1, 2, ...`.
- `removed`: how many rows of `df` are not in `latest` (a plain integer).

Use `sort_values` and `drop_duplicates(keep="last")`, not a loop. The input frame is not changed.

## Example

```python
import pandas as pd

from solution import latest_per_customer

df = pd.DataFrame({
    "row_id": [1, 2, 3, 4, 5],
    "customer": ["Ben", "Asha", "Ben", "Asha", "Ben"],
    "ts": pd.to_datetime(["2025-03-01", "2025-03-01", "2025-03-05", "2025-03-01", "2025-03-05"]),
    "amount": [10, 20, 30, 40, 50],
})
latest, removed = latest_per_customer(df)
print(latest["row_id"].tolist(), latest["customer"].tolist())
print(removed)
```

```text
[4, 5] ['Asha', 'Ben']
3
```
