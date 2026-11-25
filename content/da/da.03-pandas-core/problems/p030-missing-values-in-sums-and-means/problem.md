# Missing values in sums and means

Chapter section 11. By default pandas **skips** missing values in `sum`, `mean`, `count` and friends. That is helpful, and it
has surprises when *everything* is missing. And `nan` is never equal to anything, not even to itself.

```python
import numpy as np
import pandas as pd

s = pd.Series([1, np.nan, 3])
e = pd.Series([np.nan])

print(float(s.sum()), float(s.mean()), int(s.count()))
print(float(s.sum(min_count=1)), float(s.sum(skipna=False)))
print(float(e.sum()), float(e.sum(min_count=1)), float(e.mean()), int(e.count()))
print(np.nan == np.nan)
print((s == np.nan).tolist())
print(s.isna().tolist())
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `t = pd.Series([2, np.nan])`, `float(t.sum())` is `2.0`, `float(t.mean())` is `2.0` (the mean of the one value that
counts), and `int(t.count())` is `1`.

## After you answer

- Why is the sum of nothing `0.0` but the mean of nothing `nan`?
- Which argument turns "sum of nothing" into `nan`, and when would you want that?
- How do you test for a missing value, if `== np.nan` never works?
