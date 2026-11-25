# Every store, every month

Chapter section 6.11. A sales table only has rows for months **with** sales. A chart or a "months without sales"
report needs every store in every month, with 0 where nothing was sold. Build the full grid with a **cross join**
(every store paired with every month), then attach the sales with a **left join**.

Write `full_grid(sales, stores, months)`.

- `sales`: at most one row per store and month: `store_id`, `month` (text such as `"2025-01"`), `revenue`.
- `stores`: the store table: `store_id` (unique), `store_city`, `region`.
- `months`: a list of month texts, for example `["2025-01", "2025-02", "2025-03"]`.
- Return a frame with columns `store_id`, `month`, `revenue`: exactly one row for every store in `stores` and every
  month in `months` (so `len(stores) * len(months)` rows), `revenue` 0.0 where there was no sale. Sales for a store or
  month outside the grid are left out. Rows sorted by `store_id`, then `month`; index `0, 1, 2, ...`.

Do not change the inputs.

## Example

```python
import pandas as pd

stores = pd.DataFrame({"store_id": ["S1", "S2"], "store_city": ["Pune", "Delhi"], "region": ["west", "north"]})
sales = pd.DataFrame({"store_id": ["S1", "S2"], "month": ["2025-02", "2025-01"], "revenue": [120.0, 80.0]})
print(full_grid(sales, stores, ["2025-01", "2025-02"]))
```

```text
  store_id    month  revenue
0       S1  2025-01      0.0
1       S1  2025-02    120.0
2       S2  2025-01     80.0
3       S2  2025-02      0.0
```
