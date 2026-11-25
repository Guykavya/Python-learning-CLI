## Hint 1

`scipy.stats.chisquare(f_obs, f_exp)` needs the **expected counts**, not shares. How do you get them from the total and the planned shares?

## Hint 2

```text
counts = array; exp = counts.sum() * array(expected_share)
chi2, p = stats.chisquare(counts, exp)
verdict: "MISMATCH" if p < 0.001 else "ok"
```
