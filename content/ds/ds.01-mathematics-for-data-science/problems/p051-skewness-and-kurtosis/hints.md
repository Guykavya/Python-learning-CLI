## Hint 1

First the mean, then the central moments `m2`, `m3`, `m4`. Skewness and kurtosis are `m3` and `m4` divided by a power of `m2`, so they do not depend on the unit of the data.

## Hint 2

```text
d = x - mean(x)
m2 = mean(d**2); m3 = mean(d**3); m4 = mean(d**4)
skew = m3 / m2**1.5;  kurt = m4 / m2**2 - 3
```
