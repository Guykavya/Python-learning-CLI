## Approach

`drop(columns=...)` returns a new DataFrame, so the caller's table is untouched. Check the name first so the error says something useful.

## Code

```python
def split_xy(df, target):
    if target not in df.columns:
        raise KeyError(f"target column '{target}' not found; columns are {list(df.columns)}")
    X = df.drop(columns=[target])
    y = df[target]
    return X, y
```

## Complexity

O(n * p) to copy the features.

## Another way

`X = df.loc[:, df.columns != target]` gives the same table.
