# Per-column stats with gaps

Chapter sections 10.4 (`nan`-aware versions) and 10.6 (`out=` and `where=`). A sensor table has one row per reading and one column per sensor. Missing readings are `nan`. Write `column_stats(x)` for a 2-D array (or nested list) `x` of shape `(rows, cols)` and return a dict:

| key | value |
|---|---|
| `"count"` | number of non-`nan` values in each column, integer array of shape `(cols,)` |
| `"mean"` | mean of the non-`nan` values of each column, `float64`, shape `(cols,)` |
| `"std"` | **population** standard deviation (`ddof=0`, like `np.nanstd`) of the non-`nan` values, `float64`, shape `(cols,)` |

A column with **no** valid value (all `nan`, or a table with zero rows) has count `0`, mean `nan` and std `nan`, and your function must do this **without any RuntimeWarning**. `np.nanmean` on an all-`nan` column prints "Mean of empty slice": the test turns warnings into errors, so you have to avoid that call on such columns (or not use it at all). Integer tables are allowed (they simply have no `nan`). Do not change the caller's array.

## Example

```python
x = np.array([[1.0, np.nan, np.nan],
              [3.0, 4.0,    np.nan],
              [5.0, 8.0,    np.nan]])
s = column_stats(x)
s["count"]   # array([3, 2, 0])
s["mean"]    # array([3., 6., nan])
s["std"]     # array([1.63299316, 2.        ,        nan])
```
