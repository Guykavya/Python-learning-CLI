## Hint 1

For part 1 you only need means, a variance, a correlation and a line fit. For part 2, which of the three checks addresses which picture (a curve, an outlier, a lone far-away x)?

## Hint 2

```text
A = column_stack([ones, x]) ; line: beta = lstsq(A, y) ; r = y - A @ beta
A2 = column_stack([ones, x, x ** 2]) ; r2 = y - A2 @ lstsq(A2, y) ; reduction = 1 - (r2 ** 2).sum() / (r ** 2).sum()
H = A @ inv(A.T @ A) @ A.T ; leverage = diag(H).max()
outlier ratio = abs(r).max() / median(abs(r))
```
