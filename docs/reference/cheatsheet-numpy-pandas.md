# NumPy and pandas cheat sheet

## NumPy
```python
import numpy as np
a = np.arange(12).reshape(3, 4)       # shape (3, 4)
a[1, :]  a[:, 2]  a[a > 5]            # row, column, boolean mask
a.sum(axis=0)                          # axis=0 collapses rows (one result per column)
a + np.array([1, 2, 3, 4])             # broadcasting: shapes align from the right
np.where(a > 5, 1, 0)   np.argsort(x)   np.unique(x, return_counts=True)
```
Broadcast rule: two dimensions are compatible if equal or one of them is 1. Slices are **views** (changing them changes the original); fancy/boolean indexing returns copies.

## pandas
```python
import pandas as pd
df = pd.read_csv("f.csv", parse_dates=["day"])
df.info(); df.describe(); df.isna().sum()
df[df["age"] > 30]                         # filter
df.loc[df.age > 30, ["name", "age"]]       # label based, rows + columns
df.iloc[:5, :2]                            # position based
df.assign(rate=lambda d: d.a / d.b)        # new column without mutating
df.groupby("team").agg(n=("id", "size"), avg=("pay", "mean"))
df.merge(other, on="id", how="left", validate="m:1")
df.pivot_table(index="team", columns="year", values="pay", aggfunc="sum")
df.sort_values(["a", "b"], ascending=[True, False])
df["s"].str.lower().str.contains("x")
df["day"].dt.month
```
Traps: chained assignment (`df[a][b] = x`) may not write; use `.loc[a, b] = x`. `merge` can silently multiply rows: use `validate=`. `NaN != NaN`; use `isna()`. Check dtypes after reading a file. Row loops are slow: prefer vectorised operations.

## Plotting
`df.plot(kind="line")` · `plt.subplots()` · always label axes and units; start bars at zero.
