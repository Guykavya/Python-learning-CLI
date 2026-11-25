## Approach

Two passes: the mean, then the sum of squared deviations. The divisor is `n - ddof`. The sample version is larger because a sample's own mean is closer to the sample points than the true mean is, so dividing by `n` would underestimate the spread.

## Code

```python
import math

def variance(values, ddof):
    if ddof not in (0, 1):
        raise ValueError("ddof must be 0 (population) or 1 (sample)")
    n = len(values)
    if n - ddof < 1:
        raise ValueError(f"need more than {ddof} value(s)")
    m = sum(values) / n
    return sum((x - m) ** 2 for x in values) / (n - ddof)

def stdev(values, ddof):
    return math.sqrt(variance(values, ddof))
```

## Complexity

O(n) time, O(1) extra space.

## Another way

Welford's one-pass algorithm updates the mean and the sum of squares as each value arrives, which is useful for data streams and keeps the numerical stability. `statistics.pvariance` and `statistics.variance` are the library versions.
