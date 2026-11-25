# Pivot table with totals

Chapter section 8.3. The table `items` has one row per order line with the columns `region`, `month` (text
`"YYYY-MM"`) and `revenue` (plus maybe others). Several lines can share a region and month. Build the spreadsheet-style
report "revenue by region and month, with totals".

Write `region_month_table(items)` that returns a `pivot_table`:

- rows: the regions, sorted, plus a last row `"Total"`; columns: the months, sorted, plus a last column `"Total"`;
- each cell is the **sum** of `revenue`; a region with no sales in a month shows `0`, not `NaN`;
- the `Total` row and column are the sums across, so the bottom-right cell is the grand total of `revenue`;
- leave the index named `region` and the columns named `month` (as `pivot_table` makes them). Do not change the input.

## Example

```python
import pandas as pd

items = pd.DataFrame({"region": ["north", "north", "west"],
                      "month": ["2025-01", "2025-02", "2025-01"],
                      "revenue": [100.0, 30.0, 20.0]})
t = region_month_table(items)
print(t.index.tolist(), t.columns.tolist())
print(t.values.tolist())
```
```text
['north', 'west', 'Total'] ['2025-01', '2025-02', 'Total']
[[100.0, 30.0, 130.0], [20.0, 0.0, 20.0], [120.0, 30.0, 150.0]]
```
