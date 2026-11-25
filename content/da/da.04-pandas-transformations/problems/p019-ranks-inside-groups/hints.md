## Hint 1

Split the rows by store first and write each store's values with their row labels. Rank inside each store from the
highest revenue (`ascending=False`), then write the ranks back in the original row order.

## Hint 2

```text
S1: label 0 -> 50, label 1 -> 80, label 3 -> 80, label 6 -> 20     order: 80, 80, 50, 20
S2: label 2 -> 30, label 4 -> 90, label 5 -> 30                     order: 90, 30, 30
dense:   tied rows share a rank, next rank is +1
min:     tied rows share the lowest rank, next rank skips
first:   ties by row order (label 1 before label 3)
average: tied rows get the mean of the positions they occupy
```
