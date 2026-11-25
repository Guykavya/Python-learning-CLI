## Hint 1

What does one sample look like in code, and how do you repeat it `reps` times and collect only the means? Which object must every random call use?

## Hint 2

```text
return np.array([rng.choice(pop, n, replace=False).mean() for _ in range(reps)])
```
