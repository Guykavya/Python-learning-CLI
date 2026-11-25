## Hint 1

What do you do to the labels, and what do you keep fixed? How do you decide that a shuffled difference is "as extreme" in a two-sided test? Why is the observed arrangement one of the possible arrangements?

## Hint 2

```text
pool = np.concatenate([a, b]) ; n = len(a)
for _ in range(reps): s = rng.permutation(pool); d = s[:n].mean() - s[n:].mean(); count += abs(d) >= abs(d_obs) - 1e-12
return (1 + count) / (reps + 1)
```
