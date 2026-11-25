## Hint 1

`transform("mean")` gives every row the mean of its group, with the original index. Is there a built-in name for the
standard deviation as well? Once both are columns as long as `df`, the formula is ordinary column arithmetic.

## Hint 2

```text
g    = df.groupby(key)[col]
mean = g.transform("mean")
std  = g.transform("std")
z    = (df[col] - mean) / std       -> rename to "z"
```
