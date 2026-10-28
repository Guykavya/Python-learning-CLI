## Hint 1

Look up each key in the table: almost every one is a single call to `statistics` (`fmean`,
`median`, `multimode`, `stdev`, `pstdev`). What does `statistics.stdev([5])` do? So what must
you check first?

## Hint 2

Sample vs population: `pstdev` divides by `n` (you have the whole population), `stdev` divides by
`n - 1` (you have a sample and estimate the spread of a bigger population). For
`[2, 4, 4, 4, 5, 5, 7, 9]` they are 2.0 and 2.138.

## Hint 3

```
summary:   if not data: raise ValueError
           build the dict; stdev only if len(data) >= 2 else None
quartiles: return statistics.quantiles(data, n=4)
outliers:  q1, _, q3 = quartiles(data); iqr = q3 - q1
           low = q1 - 1.5*iqr; high = q3 + 1.5*iqr
           return [x for x in data if x < low or x > high]
```
