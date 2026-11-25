## Hint 1

How do you remove a column and get a new DataFrame back, leaving the old one alone? What does `df.pop` do to the original?

## Hint 2

```text
if target not in df.columns: raise KeyError(f"target column '{target}' not found; columns are {list(df.columns)}")
X = df.drop(columns=[target])
y = df[target]
return X, y
```
