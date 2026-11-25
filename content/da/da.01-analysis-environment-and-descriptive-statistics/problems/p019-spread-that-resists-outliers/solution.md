## Approach

Five small summaries. `range`, `sd` and `cv` use every value fully, so one extreme value dominates them; `iqr` and `mad` are built from the middle of the sorted data, so a single extreme value moves them by at most a position or so. Dividing by the mean in `cv` makes the spread unit-free (comparable between rupees and milliseconds) but only makes sense for positive data.

## Code

```python
import statistics

def describe_spread(values):
    if len(values) < 2:
        raise ValueError("need at least two values")
    s = sorted(values)
    q1, _, q3 = statistics.quantiles(s, n=4, method="inclusive")
    median = statistics.median(s)
    mean = statistics.fmean(s)
    sd = statistics.stdev(s)
    return {
        "range": s[-1] - s[0],
        "sd": sd,
        "iqr": q3 - q1,
        "mad": statistics.median(abs(x - median) for x in s),
        "cv": sd / mean if mean != 0 else None,
    }
```

## Complexity

O(n log n) for the sort.

## Another way

Compute the inclusive quartiles by hand with the formula of section 12 (position `(n - 1) * p / 100`). `scipy.stats.median_abs_deviation` also offers a scaled MAD (times 1.4826) that estimates the standard deviation for bell-shaped data.
