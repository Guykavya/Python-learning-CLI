## Hint 1

Write the log of the binomial pmf: `log C(n, k) + k log p + (n - k) log(1 - p)`. Which `math` function gives `log(m!)` for large `m`?

## Hint 2

```text
log_pmf = lgamma(n+1) - lgamma(k+1) - lgamma(n-k+1) + k*log(p) + (n-k)*log1p(-p)
return exp(log_pmf)
```
Handle `p == 0` and `p == 1` first (the result is 1 only for `k = 0`, respectively `k = n`).
