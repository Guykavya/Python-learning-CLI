## Hint 1

What is one bootstrap replicate: how many values, from where, with or without replacement? Then what do you do with `B` replicates to get an interval?

## Hint 2

```text
boots = [stat(rng.choice(x, len(x), replace=True)) for _ in range(B)]
a = (1 - level) / 2
return np.quantile(boots, a), np.quantile(boots, 1 - a)
```
