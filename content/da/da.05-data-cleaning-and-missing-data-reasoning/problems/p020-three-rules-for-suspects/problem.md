# Three rules for suspects

Chapter section 6.3. No statistic can tell a **wrong** value from a **real but extreme** one. A rule can only point at
*suspects*; a person decides. So the first habit is: **flag, look, then act**. Three standard rules:

- **IQR fences.** `Q1` and `Q3` are the 25th and 75th percentiles, `IQR = Q3 - Q1`. A value is a suspect when it is below
  `Q1 - k * IQR` or above `Q3 + k * IQR` (default `k = 1.5`). Values exactly on a fence are **not** flagged.
- **z-score.** `z = (x - mean) / std` (the sample standard deviation, pandas' default). Suspect when `|z| > t`
  (default `t = 3`). Weakness: the outliers inflate the mean and the std, so they hide themselves (**masking**).
- **Robust z-score.** `0.6745 * (x - median) / MAD`, where `MAD = median(|x - median|)`. Suspect when the absolute value is
  greater than `t` (default `t = 3.5`). The median and the MAD ignore extreme values. When `MAD` is `0` (more than half of
  the values equal the median) the score is undefined: **flag nothing**.

Write `flag_iqr(x, k=1.5)`, `flag_z(x, t=3)` and `flag_mad(x, t=3.5)`. `x` is a numeric Series (it may contain missing
values). Each returns a **Boolean Series with the same index as `x`**:

- `True` for a suspect, `False` otherwise.
- A **missing value is never flagged** (`False`), and missing values are ignored when the mean, std, median or quartiles
  are computed.
- A **constant** column has no suspects: all `False`.
- Do not change `x`.

## Example

```python
import pandas as pd

toy = pd.Series([10, 11, 9, 10, 12, 11, 10, 500, 600, 550])
print(int(flag_z(toy).sum()), int(flag_mad(toy).sum()), int(flag_iqr(toy).sum()))
print(flag_mad(toy)[flag_mad(toy)].index.tolist())

x = pd.Series([10, 12, 11, 13, 12, 11, 50, None, -30])
print(flag_iqr(x).tolist())
```

```text
0 3 0
[7, 8, 9]
[False, False, False, False, False, False, True, False, True]
```

Three clear outliers and the z-score finds **none**: the mean (172.3) and the std (261.7) were pulled up by the outliers
themselves. The IQR fences are also stretched here (Q3 is pulled up by the large values: the upper fence is 930). Only the
robust z-score, built on the median, finds them.
