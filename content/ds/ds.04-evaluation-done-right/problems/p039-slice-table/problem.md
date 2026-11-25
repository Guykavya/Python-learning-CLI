# Slice table

Chapter section 12.3. One overall score can hide a group where the model does not work at all. A **slice table** shows the score per value of a column.

Write `slice_table(frame, y, p, col)`:

- `frame` is a DataFrame aligned with the NumPy arrays `y` (0/1) and `p` (probabilities), row by row (positions)
- return a DataFrame **indexed by the values of `col`** (sorted), with the columns `rows`, `base_rate` (mean of `y`), `mean_p` (mean of `p`) and `auc`
- a slice that contains only one class gets `auc = NaN` (no crash)

## Example

```text
slice_table(test_frame, y_test, p_test, "region")
        rows  base_rate  mean_p    auc
east     323     0.229    0.238  0.774
north    298     0.211    0.226  0.705
south    306     0.258    0.240  0.777
west     273     0.264    0.240  0.488   <- the model does not work here
```
