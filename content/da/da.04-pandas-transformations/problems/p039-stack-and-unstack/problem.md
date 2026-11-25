# `stack` and `unstack`

Chapter section 8.5. `unstack` moves a level of the row index up into the columns (the **innermost** level unless you
name or number one); `stack` moves the columns back down into the innermost row level.

```python
import pandas as pd

idx = pd.MultiIndex.from_tuples(
    [("S1", "online"), ("S1", "store"), ("S2", "online"), ("S2", "store"), ("S3", "online"), ("S3", "store")],
    names=["store", "channel"])
s = pd.Series([5, 7, 2, 4, 9, 1], index=idx)

u = s.unstack()
print(u.shape, list(u.index.names), list(u.columns))

u0 = s.unstack(0)
print(u0.shape, list(u0.index.names), list(u0.columns))

print(u.loc["S2"].tolist())
print(u0.loc["store"].tolist())

back = u.stack()
print(back.shape, list(back.index.names), back.tolist())

gap = s.drop(("S3", "store")).unstack()
print(int(gap.isna().sum().sum()))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For a Series indexed by `("a", "x"), ("a", "y"), ("b", "x"), ("b", "y")` with level names `["k", "m"]`,
`unstack()` gives a 2 × 2 table with rows `a, b` (named `k`) and columns `x, y`; `unstack(0)` gives rows `x, y`
(named `m`) and columns `a, b`.

## After you answer

- Which call would you use to get one **row per channel** and one column per store?
- Why does the last line count exactly one missing cell, and what would `unstack(fill_value=0)` print there instead?
