## Hint 1

List the pieces of the sentence and where each number comes from: the clean values, the mean, the standard error, the interval ends, the rounding rule. In which order must you compute them?

## Hint 2

```text
x = np.asarray(x, float); x = x[~np.isnan(x)]; n = len(x)
se = x.std(ddof=1) / sqrt(n) ; h = t.ppf((1 + level) / 2, n - 1) * se
f"{label}: {sig_round(mean, se)}{unit} ({int(round(level * 100))}% CI {sig_round(mean - h, se)} to {sig_round(mean + h, se)}; n = {n:,})"
```
