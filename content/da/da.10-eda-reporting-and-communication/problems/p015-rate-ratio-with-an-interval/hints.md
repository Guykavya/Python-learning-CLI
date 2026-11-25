## Hint 1

Compute the two rates, their ratio, then the standard error of `log(rr)`. Why do you multiply `rr` by `exp(...)` instead of adding `1.96 x se` to `rr`?

## Hint 2

```text
check e1, e0 > 0 and e1 <= n1, e0 <= n0
rr = (e1 / n1) / (e0 / n0)
se = sqrt(1/e1 - 1/n1 + 1/e0 - 1/n0)
return rr, rr * exp(-1.96 * se), rr * exp(1.96 * se)
```
