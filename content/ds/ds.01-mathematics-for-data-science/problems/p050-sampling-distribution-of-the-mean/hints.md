## Hint 1

How many numbers do you need in total? Which `axis` of the `(reps, n)` array do you average over?

## Hint 2

```text
rng = default_rng(seed)
data = draw(rng, (reps, n))
return data.mean(axis=1)
```
