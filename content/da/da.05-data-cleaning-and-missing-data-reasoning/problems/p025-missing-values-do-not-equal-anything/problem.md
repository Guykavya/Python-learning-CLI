# Missing values do not equal anything

Chapter sections 7.2 and 7.3. `NaN` is not equal to anything, not even itself. `pd.NA` is stricter: any comparison with
it is "unknown". Aggregations skip missing values. Read the program, hand-trace it, and write **every line it prints**,
in order, in `answer.txt`.

```python
import numpy as np
import pandas as pd

f = pd.Series([4.0, 2.0, np.nan, 4.0, 4.0, 2.0])
print((f == np.nan).tolist())
print(f.isna().tolist())
print((f > 2).tolist())
print(float(f.sum()), float(f.mean()))
print(f.value_counts(dropna=False).to_dict())

g = pd.Series([4, None, 2], dtype="Int64")
print((g > 2).tolist())
print((g == pd.NA).tolist())
try:
    bool(pd.NA)
except TypeError as e:
    print(type(e).__name__)
print(int(g.sum()), float(g.mean()))
print(int(f.count()), len(f))
```

Write the lines exactly as Python prints them (`True`, `nan`, `<NA>`, dictionary braces and all).

Do not run the code before you have written your answer.

## Example

For `h = pd.Series([1.0, np.nan])`, `(h == h).tolist()` prints `[True, False]`: the missing value is not equal to itself.
`h.sum()` is `1.0` and `h.mean()` is `1.0`: both skip it.

## After you answer

- Which line of the output shows that `== np.nan` can never find missing values?
- Why does `(f > 2)` give `False` for the missing value, but `(g > 2)` gives `<NA>`?
- The mean of `f` is `3.2`, not `16 / 6`. Which number is the mean divided by?
