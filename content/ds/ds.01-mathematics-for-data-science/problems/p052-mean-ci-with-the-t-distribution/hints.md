## Hint 1

Four numbers: the mean, `s` with `ddof=1`, the standard error `s / sqrt(n)`, and the multiplier `t`. Which `q` and which `df` do you give to `t_ppf` for a 95% interval?

## Hint 2

```text
q = 0.5 + level / 2
t = t_ppf(q, n - 1)
return mean - t * se, mean + t * se
```
