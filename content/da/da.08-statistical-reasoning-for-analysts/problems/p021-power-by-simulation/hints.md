## Hint 1

What are the two random quantities per experiment, and what do you compute from them? What does "the share of experiments with p < 0.05" estimate? What do you do when the pooled standard error is zero?

## Hint 2

```text
ka = rng.binomial(n, p0, sims) ; kb = rng.binomial(n, p1, sims)
pp = (ka + kb) / (2 * n) ; se = sqrt(pp * (1 - pp) * 2 / n)
z = where(se > 0, (kb - ka) / n / se, 0) ; p = 2 * norm.sf(abs(z)) ; return mean(p < 0.05)
```
