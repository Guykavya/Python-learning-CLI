# Assigning a Series with other labels

Chapters 4.3 and 9.1. Assigning a Series to a column **aligns on the index**. `df["target"] = targets` matches the labels
of `df` (`0, 1, 2, ...`) with the labels of `targets` (here, **customer ids**). That is almost never what you want: you
get `NaN` for ids that are not row numbers, or, worse, wrong numbers when an id happens to equal a row number.

`df` has a column `customer_id` (and a default row index). `targets` is a Series of targets **indexed by customer id**.

Write `attach_targets(df, targets)` returning a tuple `(new_df, n_missing)`:

- `new_df` is a copy of `df` with a new column `target` holding, for each row, the target of that row's customer;
- a customer that has no entry in `targets` gets a missing value;
- `n_missing` is the number of **rows** whose customer has no entry in `targets` (an `int`);
- the input frame and `targets` are not changed.

## Example

```python
df = pd.DataFrame({"customer_id": [2, 0, 7, 2]})
targets = pd.Series([50, 80], index=[2, 0])
new_df, n_missing = attach_targets(df, targets)
new_df["target"].tolist()    # [50.0, 80.0, nan, 50.0]
n_missing                    # 1
```

A plain `df["target"] = targets` would give `[80.0, nan, 50.0, nan]`: row 0 gets the target labelled 0 (customer 0's, not
its own), row 2 gets the target labelled 2, and so on: alignment by **row number**.
