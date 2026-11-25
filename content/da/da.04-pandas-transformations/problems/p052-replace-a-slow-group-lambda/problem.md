# Replace a slow group lambda

Chapter sections 4.1 and 12.2. A colleague standardises revenue inside each store (a **z-score**: how many standard
deviations a line is above its store's mean) with this line:

```text
z = df.groupby(key)[col].transform(lambda s: (s - s.mean()) / s.std())
```

It is correct, but it calls a Python function once per group. With thousands of groups it is slow.

Write `zscore_by_group(df, key="store_id", col="revenue")` that returns the **same** numbers using only built-in group
transforms (no `lambda`, no `apply`, no loop):

- a Series with the same index as `df` (in the same order), named `"z"`;
- `(value - group mean) / group standard deviation`, with pandas' default standard deviation (`ddof=1`); a group with
  a single row has no standard deviation, so its z-score is `NaN`, exactly as in the slow line;
- do not change the input.

The tests compare with the slow line, and time both on 300,000 rows in 2,000 groups **in the same run**: yours must be
at least 5 times faster than the lambda (in the chapter's measurement the built-ins were about 23 times faster;
timings are machine-specific, the ratio is what counts).

## Example

```python
import pandas as pd

df = pd.DataFrame({"store_id": ["S1", "S1", "S1", "S2"], "revenue": [10.0, 20.0, 30.0, 5.0]},
                  index=[7, 3, 9, 1])
z = zscore_by_group(df)
print(z.name, z.index.tolist(), z.tolist())
```
```text
z [7, 3, 9, 1] [-1.0, 0.0, 1.0, nan]
```
