## Approach

The two functions are short; the thinking is in the tests. With a sample standard deviation, a single value in a list of `n` can have a z-score of at most `(n - 1) / sqrt(n)`, so for `n = 8` it can never exceed 2.47 and the 3-sigma rule is **blind** whatever the data. And when two values are large, both inflate the sd and shrink each other's z. The quartiles ignore the top and bottom quarters, so the IQR fences are not moved by them.

## Code

```python
import statistics

def flag_iqr(values, k=1.5):
    if len(values) < 2:
        return []
    q1, _, q3 = statistics.quantiles(values, n=4, method="inclusive")
    iqr = q3 - q1
    low, high = q1 - k * iqr, q3 + k * iqr
    return [i for i, x in enumerate(values) if x < low or x > high]

def flag_z(values, t=3):
    if len(values) < 2:
        return []
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)
    if sd == 0:
        return []
    return [i for i, x in enumerate(values) if abs(x - mean) / sd > t]
```

## Complexity

O(n log n) for `flag_iqr` (quantiles sort), O(n) for `flag_z`.

## Another way

A **robust z-score** uses the median and the MAD instead: `0.6745 * (x - median) / MAD`, flagged above 3.5. It keeps the z-score's scale without letting the outliers inflate it.
