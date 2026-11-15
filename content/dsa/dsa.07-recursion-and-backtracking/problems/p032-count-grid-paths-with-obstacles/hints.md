## Hint 1

`go(r, c)` = number of paths from `(r, c)` to the end that avoid the cells already on the current path. What does it return at the end cell?

## Hint 2

Mark `(r, c)` as visited, sum `go` over the free, unvisited neighbours, then un-mark `(r, c)` and return the sum.

## Hint 3

```
def go(r, c):
    if (r, c) == end: return 1
    visited[r][c] = True
    total = 0
    for each neighbour (nr, nc) inside, free and not visited: total += go(nr, nc)
    visited[r][c] = False
    return total
```
