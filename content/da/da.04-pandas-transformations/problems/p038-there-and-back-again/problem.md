# There and back again

Chapter section 8.4 ends with a round trip: `melt` and `pivot` are inverses **when the data are complete**. Real data
are not complete, and a reshape that quietly changes a type or invents a row is a bug. Write two functions that are
exact inverses of each other.

The **long** table has the columns `store_id` (text), `month` (text `"YYYY-MM"`) and `sales` (whole numbers, `int64`).
Each (store, month) pair appears at most once, and some pairs are simply absent (no row).

- `to_wide(long)` returns `store_id` as the first column, then one column per month in sorted order, one row per
  store (sorted), a fresh index, no name on the column labels. An absent pair is `NaN`.
- `to_long(wide)` returns the columns `store_id`, `month`, `sales`, sorted by store then month, fresh index. **Missing
  cells are dropped** (they were absent pairs), and `sales` is `int64` again.

So, for every long table of this kind, `to_long(to_wide(long))` equals the long table sorted by store and month, with
the same dtypes. And for every wide table whose rows and month columns each have at least one value,
`to_wide(to_long(wide))` equals the wide table. The tests check both on 20 random tables. Do not change the inputs.

## Example

```python
import pandas as pd

long = pd.DataFrame({"store_id": ["S1", "S2", "S1"], "month": ["2025-01", "2025-02", "2025-02"], "sales": [10, 7, 4]})
w = to_wide(long)
print(w.values.tolist())
back = to_long(w)
print(back.values.tolist(), back["sales"].dtype)
```
```text
[['S1', 10.0, 4.0], ['S2', nan, 7.0]]
[['S1', '2025-01', 10], ['S1', '2025-02', 4], ['S2', '2025-02', 7]] int64
```
