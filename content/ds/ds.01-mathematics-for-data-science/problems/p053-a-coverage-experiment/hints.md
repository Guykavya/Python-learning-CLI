## Hint 1

One repetition: draw a sample, compute the interval, check `low <= 0 <= high`. How do you turn all the checks into one fraction?

## Hint 2

```text
hits = 0
for _ in range(reps): sample = rng.normal(size=n); lo, hi = ci_fn(sample); hits += lo <= 0 <= hi
return hits / reps
```
