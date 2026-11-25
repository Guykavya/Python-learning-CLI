# Worst slices scan

Chapter section 12.4. Looking at one column at a time by hand misses things. Scan **every single column and every pair of columns**, keep slices with enough rows, and rank them by how much **worse** the model does there than overall.

Write `worst_slices(frame, y, p, cols, min_rows=120, top=6)` returning a DataFrame with the columns `slice, rows, gap`:

- the overall score is `log_loss(y, p)`
- for every single column in `cols` and every pair (`itertools.combinations(cols, 2)`), group `frame` by those columns; skip a group with fewer than `min_rows` rows or with only one class in `y`
- the slice name is `"col=value"` for one column and `"col1=value1 & col2=value2"` for a pair
- `gap` = `log_loss(y[idx], p[idx], labels=[0, 1])` minus the overall log loss
- sort by `gap`, largest first, and return the first `top` rows with a fresh index `0, 1, ...`

`frame` is aligned with `y` and `p` by position.

## Example

```text
worst_slices(test_frame, y, p, ["region", "contract"])
                         slice  rows   gap
                   region=west   612  0.144
  region=west & contract=month   361  0.122
  region=east & contract=month   335  0.111
```
