# Find exact and near duplicates

Chapter section 5. Duplicate rows that land on both sides of a split let the model "remember" the answer. Some copies are exact; others differ only in the last decimal (a re-export, a currency conversion).

Write `duplicate_groups(df, cols, round_to=2)` returning a `pandas.Series` of integer **group ids**, aligned with `df.index`:

- two rows are in the same group when they are equal on every column in `cols` after rounding the **numeric** columns to `round_to` decimals (other columns are compared as they are);
- ids are numbered `0, 1, 2, ...` in order of **first appearance** in `df`;
- `df` itself is not modified.

## Example

```text
   a       b
0  1.000   x      -> group 0
1  2.000   y      -> group 1
2  1.0004  x      -> group 0   (equal to row 0 after rounding to 2 decimals)
3  1.000   z      -> group 2
```
