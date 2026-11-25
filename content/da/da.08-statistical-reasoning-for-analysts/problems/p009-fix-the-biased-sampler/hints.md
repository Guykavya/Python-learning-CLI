## Hint 1

What do you want instead of "the first n rows": n row positions chosen at random, all different? Which method of `rng` picks positions without repeating any?

## Hint 2

```text
idx = rng.choice(len(pop), n, replace=False)
return pop.iloc[idx]
```
