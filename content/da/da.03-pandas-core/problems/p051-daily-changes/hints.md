## Hint 1

Section 16.4 shows `diff`, `pct_change` and `cumsum`. What does `pct_change` give when yesterday was `0`? And what does the statement want in that case? Which method replaces specific values (here `inf` and `-inf`) by something else?

## Hint 2

```text
diff          = s.diff()
pct_change    = s.pct_change().replace([np.inf, -np.inf], np.nan)
running_total = s.cumsum()
return pd.DataFrame({"diff": ..., "pct_change": ..., "running_total": ...})
```
The first row of `diff` and `pct_change` is already `NaN`: there is no yesterday.
