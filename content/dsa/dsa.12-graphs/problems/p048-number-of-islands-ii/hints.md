## Hint 1

Keep the number of islands as a running counter. What happens to it when a lonely land cell appears? When that cell touches one island? Two different islands? One island from two sides?

## Hint 2

Use a DSU over the `rows * cols` flat indices plus a set (or list of booleans) `land`. For a new cell: if it is already land, append the current count and continue. Otherwise mark it, `count += 1`, and for each of the 4 neighbours **inside the map** that is land: `if union(cell, neighbour): count -= 1` (`union` returns `True` only when it merged two different groups).

## Hint 3

```
parent = list(range(rows * cols)); land = [False] * (rows * cols); count = 0; out = []
for r, c in positions:
    i = r * cols + c
    if not land[i]:
        land[i] = True; count += 1
        for nr, nc in ((r+1, c), (r-1, c), (r, c+1), (r, c-1)):
            if 0 <= nr < rows and 0 <= nc < cols and land[nr * cols + nc]:
                if union(i, nr * cols + nc): count -= 1
    out.append(count)
return out
```
