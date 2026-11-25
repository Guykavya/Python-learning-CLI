## Hint 1

For one world, write the generating step as a few lines inside a loop. Which random calls need to be inside the loop, and which object must be created *outside* it?

## Hint 2

```text
rng = default_rng(seed); hits = 0
repeat reps times:
    x, e = draw according to the world
    y = 1 + 2x + e
    fit = OLS(y, add_constant(x)).fit(cov_type="HC3" if robust)
    lo, hi = conf_int()[1]          # row 1 is the slope
    hits += lo <= 2 <= hi
return hits / reps
```
The AR(1) errors need a small loop over t.
