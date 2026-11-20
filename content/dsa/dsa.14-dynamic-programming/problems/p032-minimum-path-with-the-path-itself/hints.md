## Hint 1

First fill the table `f` exactly as in minimum path sum: `f[r][c]` = the cheapest cost from the start to `(r, c)`. The total is `f[rows-1][cols-1]`. Now the path: the best path into `(r, c)` came from the neighbour (above or left) with the **smaller `f`**. Why the smaller `f`, and not the smaller `grid` value?

## Hint 2

Walk back from the bottom-right cell. On the first row you can only step left; on the first column, only up; elsewhere step to the neighbour with the smaller `f` (on a tie either is fine). Append each cell. Stop at `(0, 0)`. The list is now end-to-start: reverse it.

## Hint 3

```
fill f
r, c = rows-1, cols-1;  route = [(r, c)]
while (r, c) != (0, 0):
    if r == 0:                    c -= 1
    elif c == 0:                  r -= 1
    elif f[r-1][c] <= f[r][c-1]:  r -= 1
    else:                         c -= 1
    route.append((r, c))
route.reverse()
return f[rows-1][cols-1], route
```
