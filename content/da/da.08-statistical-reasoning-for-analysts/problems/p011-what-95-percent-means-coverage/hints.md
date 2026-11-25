## Hint 1

What do you count in each repetition, and what do you divide by at the end? Where must the randomness come from?

## Hint 2

```text
hits = 0
for _ in range(reps): lo, hi = ci_fn(sampler(rng)); hits += lo <= truth <= hi
return hits / reps
```
