# Binomial and Poisson pmfs

Chapter section 11.3. The **binomial** pmf is `P(K = k) = C(n, k) p^k (1 - p)^(n - k)`; the **Poisson** pmf is `P(K = k) = lam^k e^(-lam) / k!`. For large `n` the pieces overflow (`C(5000, 2500)` has about 1,500 digits), so work with **logarithms** (`math.lgamma(m + 1)` is `log(m!)`) and exponentiate at the end.

Write `binom_pmf(k, n, p)` and `poisson_pmf(k, lam)`. Both return `0.0` for `k` outside the possible range (`k < 0`, or `k > n` for the binomial). Handle `p = 0`, `p = 1` and `lam = 0` without taking `log(0)`.

## Example

```text
binom_pmf(1, 2, 0.5)     ->  0.5
poisson_pmf(0, 2.0)      ->  0.1353     (e^-2)
binom_pmf(2500, 5000, 0.5) -> 0.01128   (no overflow)
```
