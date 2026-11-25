## Hint 1

Start with a small table per store: its rows (labels), its values, its sum, its mean and its size. Every line of the
program can be answered from that table.

## Hint 2

```text
S1: labels 0, 2, 5, 7  rev 10, 20, 30, 40  sum 100  mean 25  size 4
S2: labels 1, 4        rev 40, 50          sum  90  mean 45  size 2
S3: labels 3, 6        rev  5, 15          sum  20  mean 10  size 2
agg       -> one value per store, stores sorted
transform -> the store's value written on each of the 8 rows, in row order
filter / mask -> original row labels of the stores that pass
head(1)   -> the first row of each group
```
