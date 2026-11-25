## Hint 1

You do not need a loop over the looks: take cumulative sums of the Bernoulli draws along each row and read them at the look points. How do you turn "any look significant" into one boolean per simulation?

## Hint 2

```text
a = rng.random((n_sims, n)) < p; b = ...
ka = a.cumsum(axis=1)[:, ns - 1]; kb = ...  with ns = per_look * arange(1, looks + 1)
z -> sig = |z| > 1.96   (shape n_sims x looks)
fixed = sig[:, -1].mean(); peek = sig.any(axis=1).mean()
```
