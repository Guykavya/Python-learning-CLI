## Hint 1

The mean is a weighted average. Once you have it, the variance is the weighted average of the squared distances from it.

## Hint 2

```text
check lengths, check all p >= 0, check |sum(p) - 1| < 1e-9
mean = sum(x * p); var = sum((x - mean)**2 * p)
```
