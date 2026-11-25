# Columns with a shared stem

Chapter section 8.9. An old report has one row per store and columns such as `sales_2023`, `sales_2024`,
`units_2023`, `units_2024`. The column **names** hide two variables (sales, units) and one key (the year).

Write `yearly_long(df)`:

- the input has a column `store_id` (one row per store) and, for every year in the report, one `sales_<year>` and one
  `units_<year>` column (the years and their number vary from file to file; the columns may come in any order);
- return one row per store and year with exactly the columns `store_id`, `year` (an integer), `sales`, `units`;
- rows sorted by `store_id`, then `year`; fresh index `0, 1, ...`; do not change the input.

The tests compare your answer with a plain loop over the columns on many random reports.

## Example

```python
import pandas as pd

df = pd.DataFrame({"store_id": ["S2", "S1"], "sales_2023": [200, 100], "units_2023": [20, 10],
                   "sales_2024": [190, 110], "units_2024": [18, 12]})
out = yearly_long(df)
print(out.values.tolist())
print(out.dtypes.astype(str).tolist())
```
```text
[['S1', 2023, 100, 10], ['S1', 2024, 110, 12], ['S2', 2023, 200, 20], ['S2', 2024, 190, 18]]
['str', 'int64', 'int64', 'int64']
```
