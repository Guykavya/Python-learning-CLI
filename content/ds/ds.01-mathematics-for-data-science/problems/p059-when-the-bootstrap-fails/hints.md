## Hint 1

This is problem 53 (coverage) with problem 58 (bootstrap interval) inside the loop. Which two random generators can you replace by one?

## Hint 2

```text
for _ in range(reps):
    x = draw(rng, n)
    boots = [stat(x[rng.integers(0, n, n)]) for _ in range(boot_reps)]
    lo, hi = quantile(boots, [0.025, 0.975])
    hits += lo <= truth <= hi
```
