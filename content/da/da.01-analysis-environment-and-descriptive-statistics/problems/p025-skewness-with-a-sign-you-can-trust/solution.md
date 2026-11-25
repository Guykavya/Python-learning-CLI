## Approach

The cube of a z-score is negative below the mean and positive above it, and large for far values, so a long tail dominates the sum. The result does not depend on the unit or the origin: `skewness([a * x + b ...])` equals `skewness(values)` for `a > 0`, and flips sign for `a < 0`, which is why a mirrored list gives exactly the negative.

## Code

```python
import math

def skewness(values):
    n = len(values)
    if n < 3:
        raise ValueError("need at least 3 values")
    m = sum(values) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in values) / n)
    if sd == 0:
        raise ValueError("all values are equal: skewness is undefined")
    return sum(((x - m) / sd) ** 3 for x in values) / n
```

## Complexity

O(n).

## Another way

The **sample-adjusted** skewness (as in Excel's `SKEW` or pandas) multiplies by `sqrt(n * (n - 1)) / (n - 2)` and differs for small `n`; the chapter's population formula is the simplest to state and test.
