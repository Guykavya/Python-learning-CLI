## Approach

Each method returns a new frame, so they chain. `rename(columns=function)` applies the function to every name. After renaming, the helper columns are recognised by their new names (`tmp_...`), and `loc[:, boolean_mask_over_columns]` keeps the others. `assign` with a lambda uses the columns of the frame **as built so far**, so `qty` and `unit_price` are already the snake_case names. The original frame is never touched.

## Code

```python
def snake(name):
    return name.strip().lower().replace(" ", "_")


def prepare(df):
    return (df.rename(columns=snake)
              .loc[:, lambda d: ~d.columns.str.startswith("tmp_")]
              .assign(revenue=lambda d: d["qty"] * d["unit_price"]))
```

## Complexity

O(rows x kept columns) for the copy; `revenue` is one vectorised multiplication.

## Another way

Compute the list first: `drop_me = [c for c in renamed.columns if c.startswith("tmp_")]` then `renamed.drop(columns=drop_me)`. With the new `pd.col` the last step is `.assign(revenue=pd.col("qty") * pd.col("unit_price"))`.
