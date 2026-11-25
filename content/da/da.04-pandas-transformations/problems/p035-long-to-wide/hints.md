## Hint 1

`pivot` needs three choices: which column becomes the rows, which the columns, which the cells. How can you find the
pairs that appear more than once *before* calling it? (`duplicated` takes a `subset=` and `keep=False`.)

## Hint 2

```text
dup = monthly[monthly.duplicated(subset=["store_id", "month"], keep=False)]
if dup is not empty: raise ValueError(f"repeated pairs {first pair}: use pivot_table(aggfunc=...)")
wide = monthly.pivot(index="store_id", columns="month", values="sales")
wide = wide.reset_index(); wide.columns.name = None
```
