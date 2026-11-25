## Hint 1

Split the table into the two hospitals first. In each, list the treated and the untreated scores and take the means. Then do the whole table.

## Hint 2

```text
all treated: 88, 58, 60, 62 -> mean 67.0 ; all untreated: 78, 80, 82, 50 -> mean 72.5 ; naive = -5.5
big: treated 88 ; untreated mean of 78, 80, 82 = 80 -> 8.0
small: treated mean of 58, 60, 62 = 60 ; untreated 50 -> 10.0
weights: both hospitals have 4 rows -> (8 * 4 + 10 * 4) / 8
```
