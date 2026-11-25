# Wide to long

Chapter sections 8.1 and 8.4. A spreadsheet arrives **wide**: a column `store_id`, then one column per month named
`"YYYY-MM"` (not necessarily in calendar order). For a `groupby` or a chart you need it **long**.

Write `to_long(wide)` that returns a frame with exactly the columns `store_id`, `month`, `sales`:

- one row per store and month column, so `len(result) == stores × months`;
- a missing cell in the wide table stays a row with missing `sales` (do not drop or fill it here);
- rows sorted by `store_id`, then by `month` in calendar order, with a fresh index `0, 1, 2, ...`.

Do not change the input.

## Example

```python
import pandas as pd

wide = pd.DataFrame({"store_id": ["S2", "S1"], "2025-02": [5, 1], "2025-01": [7, 2]})
out = to_long(wide)
print(out.values.tolist())
```
```text
[['S1', '2025-01', 2], ['S1', '2025-02', 1], ['S2', '2025-01', 7], ['S2', '2025-02', 5]]
```
