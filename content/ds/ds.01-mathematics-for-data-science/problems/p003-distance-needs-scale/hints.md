## Hint 1

For one column the standardised value is `(x - mean) / std`. Which NumPy argument computes the mean of every column at once? What will you do if `std` is 0?

## Hint 2

```text
mean = X.mean(axis=0); std = X.std(axis=0)
std = where(std == 0, 1, std)       # constant column: avoid 0/0
return (X - mean) / std
```
For the distances: subtract row 0 from the other rows, square, sum along `axis=1`, square root.
