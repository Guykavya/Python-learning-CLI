- **Expecting a `NaN` group by default.** The default is `dropna=True`: the rows vanish silently.
- **Putting the missing group first.** With `dropna=False` pandas sorts the real keys and puts the missing key last.
- **`size()` counting the missing rows.** `size()` counts rows *in each group*, and the missing-key rows are in no group
  unless `dropna=False`.
- **Confusing `Series.count()` with `len()`.** `count()` skips missing values: 4, while `len(t)` is 6.
