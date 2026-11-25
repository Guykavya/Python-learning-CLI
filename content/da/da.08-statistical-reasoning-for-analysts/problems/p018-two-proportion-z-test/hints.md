## Hint 1

What proportion do both groups share if there is no difference, and where does it appear in the standard error? Which side of the difference is positive?

## Hint 2

```text
pA = kA / nA ; pB = kB / nB ; p = (kA + kB) / (nA + nB)
se = sqrt(p * (1 - p) * (1 / nA + 1 / nB)) ; z = (pA - pB) / se
p_value = 2 * (1 - stats.norm.cdf(abs(z)))
```
