## Hint 1

What are the two fences, and which quantiles do they need? For each strategy, which values go into the mean and the
median: all of them, only the unflagged ones, or all of them with some replaced? Which pandas methods replace values
by a boundary, and which method replaces only where a mask is `True`?

## Hint 2

```text
q1, q3 = s.quantile([0.25, 0.75]);  lo = q1 - 1.5*(q3-q1);  hi = q3 + 1.5*(q3-q1)
keep      = s
remove    = s[~flags]
cap       = s.where(~flags, s.clip(lo, hi))     # clip only where flagged
flag_only = s    (+ n_flagged = int(flags.sum()))
each -> {"mean": float(x.mean()), "median": float(x.median())}
```
