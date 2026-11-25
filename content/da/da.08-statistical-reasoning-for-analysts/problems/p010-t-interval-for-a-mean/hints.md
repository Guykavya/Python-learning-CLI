## Hint 1

Which three numbers do you need: the mean, the standard error, and a multiplier? Where does the multiplier come from, and what are its degrees of freedom?

## Hint 2

```text
n = len(x); se = x.std(ddof=1) / sqrt(n)
t = stats.t.ppf((1 + level) / 2, df=n - 1)
return mean - t * se, mean + t * se
```
