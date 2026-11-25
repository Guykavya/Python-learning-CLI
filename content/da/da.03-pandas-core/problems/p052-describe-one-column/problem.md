# Describe one column

Chapter sections 16.1 and 16.3, and da.01 (the same numbers, computed by hand). Write `describe_column(s)` for a
numeric Series that may contain missing values. It returns a dict with these keys:

| key | meaning |
|---|---|
| `n` | the number of values that are **not** missing (an `int`) |
| `missing` | the number of missing values (an `int`) |
| `mean`, `median` | the usual |
| `sd` | the **sample** standard deviation (divide by n - 1) |
| `q1`, `q3` | the quartiles with linear interpolation (what `quantile` gives; the same numbers as `statistics.quantiles(..., method="inclusive")`) |
| `skew` | the **sample** skewness (the adjusted Fisher-Pearson coefficient that `Series.skew()` gives) |

All statistics ignore the missing values. They are plain Python floats. Where a statistic does not exist the value is
`None`: with **no** values every statistic is `None`; with one value `sd` and `skew` are `None` (and `q1` and `q3`
equal the value); with two values `skew` is `None`. Use the pandas methods; do not loop. The input is not changed.

## Example

```python
import pandas as pd

from solution import describe_column

s = pd.Series([10, 15, 20, 25, 100, None])
d = describe_column(s)
print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()})
```

```text
{'n': 5, 'missing': 1, 'mean': 34.0, 'median': 20.0, 'sd': 37.3162, 'q1': 15.0, 'q3': 25.0, 'skew': 2.1116}
```
