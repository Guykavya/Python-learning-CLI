## Hint 1

Which number does `fillna` need, and which pandas method gives the mean of the values that are present? Does that mean
change after the fill? In what order must you compute the first standard deviation: before or after filling?

## Hint 2

```text
m = s.mean()                        # mean of the observed values (missing are skipped)
filled = s.fillna(m)                # a new Series
sd_before = float(s.std())          # of the observed values
sd_after  = float(filled.std())
return filled, sd_before, sd_after
```
