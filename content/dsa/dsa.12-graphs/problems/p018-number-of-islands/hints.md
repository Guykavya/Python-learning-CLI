## Hint 1

Scan the cells row by row. When you meet land that no search has visited yet, you have found a new island: count it, then visit **all** of its land so that you do not count it again. What do you need to remember for every cell?

## Hint 2

```
seen = [[False] * cols for _ in range(rows)]; count = 0
for r in range(rows):
    for c in range(cols):
        if grid[r][c] == "1" and not seen[r][c]:
            count += 1; seen[r][c] = True; stack = [(r, c)]
            while stack:
                cr, cc = stack.pop()
                for nr, nc in the 4 neighbours:
                    if inside and grid[nr][nc] == "1" and not seen[nr][nc]:
                        seen[nr][nc] = True; stack.append((nr, nc))
return count
```
