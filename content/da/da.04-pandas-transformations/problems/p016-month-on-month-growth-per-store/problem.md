# Month-on-month growth per store

Chapter section 5.1. `groupby(...).pct_change()` compares each month with the previous month **of the same store**.
Watch the zeros: growth from a month with revenue 0 is a division by zero. pandas gives `inf` for `x / 0` and `NaN`
for `0 / 0`, and an `inf` in a report breaks every average taken from it.

Write `store_growth(monthly)`. `monthly` has columns `store_id`, `month` (text such as `"2025-03"`) and `revenue`,
one row per store and month, in any order. Return a **new** frame:

- sorted by `store_id`, then `month`; index `0, 1, 2, ...`;
- with an extra column `growth_pct`: `(revenue / previous revenue − 1) × 100`, where "previous" is the store's
  previous row (month);
- `growth_pct` is **missing** for each store's first month and whenever the previous revenue is 0 (never `inf`).

Do not change `monthly`.

## Example

```python
import pandas as pd

monthly = pd.DataFrame({
    "store_id": ["S1", "S1", "S1", "S1", "S2"],
    "month": ["2025-02", "2025-01", "2025-04", "2025-03", "2025-01"],
    "revenue": [150.0, 100.0, 60.0, 0.0, 80.0],
})
print(store_growth(monthly))
```

```text
  store_id    month  revenue  growth_pct
0       S1  2025-01    100.0         NaN
1       S1  2025-02    150.0        50.0
2       S1  2025-03      0.0      -100.0
3       S1  2025-04     60.0         NaN
4       S2  2025-01     80.0         NaN
```
