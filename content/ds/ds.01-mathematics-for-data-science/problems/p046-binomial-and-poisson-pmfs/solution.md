## Approach

Work with logarithms of the big pieces, add them, and exponentiate once.

## Code

```python
import math


def binom_pmf(k, n, p):
    if k < 0 or k > n:
        return 0.0
    if p == 0:
        return 1.0 if k == 0 else 0.0
    if p == 1:
        return 1.0 if k == n else 0.0
    logp = (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
            + k * math.log(p) + (n - k) * math.log1p(-p))
    return math.exp(logp)


def poisson_pmf(k, lam):
    if k < 0:
        return 0.0
    if lam == 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(k * math.log(lam) - lam - math.lgamma(k + 1))
```

## Complexity

O(1) per call.

## Another way

Compute `P(k+1)` from `P(k)` with the ratio `(n - k) p / ((k + 1) (1 - p))` to fill a whole table cheaply.
