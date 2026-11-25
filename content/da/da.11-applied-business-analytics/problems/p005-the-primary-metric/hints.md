## Hint 1

Two standard errors: one **unpooled** for the interval (it describes the difference as estimated), one **pooled** for the test (it assumes the null hypothesis that both groups share one rate). Which goes where?

## Hint 2

```text
pA, pB = kA/nA, kB/nB; diff = pB - pA
se = sqrt(pA(1-pA)/nA + pB(1-pB)/nB); z = norm.ppf(1 - (1-level)/2)
pp = (kA + kB)/(nA + nB); z_stat = diff / sqrt(pp(1-pp)(1/nA + 1/nB)); p = 2 * norm.sf(abs(z_stat))
```
