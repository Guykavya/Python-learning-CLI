## Hint 1

Which array do you shuffle: the two groups separately, or all values together? What does shuffling do to the link between value and group?

## Hint 2

```text
pooled = concatenate([a, b]); rng = default_rng(seed)
for _ in range(reps):
    rng.shuffle(pooled); diff = mean(pooled[:na]) - mean(pooled[na:])
    count += abs(diff) >= abs(obs) - 1e-12
p = (count + 1) / (reps + 1)
```
