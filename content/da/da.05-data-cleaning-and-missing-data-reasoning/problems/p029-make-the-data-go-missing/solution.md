## Approach

The three mechanisms differ only in the **weight** of each row; everything else is shared. Scaling the weights by
`rate / mean(w)` makes the average hiding probability equal to `rate`, so all three mechanisms lose about the same share
(like the three variants of the chapter), and what differs is **who** is missing. One call `rng.random(n)` gives the
uniform numbers, so the result depends only on the generator.

## Code

```python
import numpy as np


def simulate_missing(pop, mechanism, rate, rng):
    out = pop.copy()
    n = len(out)
    if mechanism == "MCAR":
        w = np.ones(n)
    elif mechanism == "MAR":
        w = np.where(out["age"] < 40, 2.0, 1.0)
    elif mechanism == "MNAR":
        w = np.where(out["income"] > out["income"].median(), 5.0, 1.0)
    else:
        raise ValueError(f"unknown mechanism {mechanism!r}")
    p = np.clip(rate * w / w.mean(), 0, 1)
    hide = rng.random(n) < p
    out.loc[hide, "income"] = np.nan
    return out
```

## Complexity

O(n): a few vectorised passes (the median is O(n) on average).

## Another way

Draw a fixed number of victims instead (`rng.choice(n, size=round(rate*n), replace=False, p=p/p.sum())`) when you
want the share to be exactly the target. The independent draw above is closer to how real non-response behaves: the
share itself is random.
