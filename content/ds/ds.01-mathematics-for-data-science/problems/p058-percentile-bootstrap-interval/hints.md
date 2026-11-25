## Hint 1

Where does the randomness come from? Which array do you index, and how many times? What do you do with the `reps` numbers you collect?

## Hint 2

```text
stats = [stat(x[rng.integers(0, n, n)]) for _ in range(reps)]
a = (1 - level) / 2
return quantile(stats, a), quantile(stats, 1 - a)
```
