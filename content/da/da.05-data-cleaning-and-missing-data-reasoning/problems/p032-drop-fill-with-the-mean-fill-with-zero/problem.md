# Drop, fill with the mean, fill with zero

Chapter sections 9.1 and 9.4. The same eight values, three treatments of the three missing ones, and three different
sets of statistics. Read the program, hand-trace it, and write **every line it prints**, in order, in `answer.txt`.

```python
import numpy as np
import pandas as pd

v = pd.Series([4, np.nan, 8, 6, np.nan, 10, 2, np.nan])
for name, t in [("dropna", v.dropna()), ("mean", v.fillna(v.mean())), ("zero", v.fillna(0))]:
    print(name, len(t), f"{t.mean():.2f} {t.std():.2f}")
print(int(v.count()), len(v))
```

Hints for the trace (not the answer): `std()` is the **sample** standard deviation (divide by `n - 1`), and the
statistics of a Series skip missing values. Round to 2 decimals as the program does.

Do not run the code before you have written your answer.

## Example

For `w = pd.Series([1.0, 3.0, np.nan])`: `w.dropna()` has 2 values, mean 2.00, std 1.41; `w.fillna(w.mean())` has 3
values (1, 3, 2), mean 2.00, std 1.00. The line printed for the second one would be `mean 3 2.00 1.00`.

## After you answer

- Which two treatments give the same mean, and which one changes it?
- Which treatment has the smallest standard deviation, and why?
- Which treatment would you never use for a measurement that can be zero, and why?
