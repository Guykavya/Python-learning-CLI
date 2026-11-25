## Hint 1

Go through the columns from left to right and keep a `row` counter. In each column, look at the entries from `row` downwards: if the biggest one is below the tolerance, this column has no pivot, so move on without advancing `row`.

## Hint 2

```text
r = 0
for each column c (while r < m):
    p = row at or below r with the largest |A[., c]|
    if |A[p, c]| <= tol: continue
    swap rows r and p; eliminate below; r += 1
return r
```
