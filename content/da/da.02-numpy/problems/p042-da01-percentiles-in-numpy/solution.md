## Approach

Map names, check arguments, delegate. Ch. 14.2 measured that NumPy's default `"linear"` equals `statistics`' `"inclusive"`, and `"weibull"` equals its default exclusive method. Nearest rank is NumPy's `"inverted_cdf"`: the smallest data value whose share of the data at or below it reaches `p` percent, which is exactly "rank = ceil(p·n/100), at least 1". The neighbours that look similar are different rules: `"lower"` and `"nearest"` start from the linear position `(n - 1)·p/100`, so they disagree with nearest rank on many inputs (the random test finds such cases).

NumPy's `weibull` never raises: it clamps extreme positions to the smallest or largest value. The da.01 definition raises, so the position check happens before the call.

## Code

```python
import numpy as np

NUMPY_METHOD = {
    "inclusive": "linear",
    "exclusive": "weibull",
    "nearest_rank": "inverted_cdf",
}


def percentile(x, p, method="inclusive"):
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        raise ValueError("no data")
    if not 0 <= p <= 100:
        raise ValueError(f"p={p} must be between 0 and 100")
    if method not in NUMPY_METHOD:
        raise ValueError(f"unknown method {method!r}; use one of {sorted(NUMPY_METHOD)}")
    if method == "exclusive":
        pos = (x.size + 1) * p / 100
        if pos < 1 or pos > x.size:
            raise ValueError(f"position {pos} is outside 1..{x.size} for the exclusive method")
    return float(np.percentile(x, p, method=NUMPY_METHOD[method]))
```

## Complexity

O(n) on average: `np.percentile` uses a partial sort (partition), not a full sort.

## Another way

`np.quantile(x, p / 100, method=...)` takes the fraction instead of the percent. And in pandas (da.03) `Series.quantile(q, interpolation=...)` offers `"linear"`, `"lower"`, `"higher"`, `"nearest"` and `"midpoint"` only: there is no nearest-rank option, which is one reason to know what each name means.
