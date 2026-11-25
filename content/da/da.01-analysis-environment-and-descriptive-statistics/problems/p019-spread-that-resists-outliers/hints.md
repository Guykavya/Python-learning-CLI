## Hint 1

Which of the five numbers need the median, which need the quartiles, and which need only the mean? Write the easy ones first, then check `iqr` against a hand calculation: for `[2, 4, 4, 4, 5, 5, 7, 9]` the inclusive positions are 1.75 and 5.25 (0-based): what values do they give?

## Hint 2

```text
s = sorted(values); n = len(s)
q1, _, q3 = statistics.quantiles(s, n=4, method="inclusive")   (or compute by hand)
median = statistics.median(s)
mad = statistics.median(abs(x - median) for x in s)
sd = statistics.stdev(s); mean = statistics.fmean(s)
cv = sd / mean if mean != 0 else None
```
