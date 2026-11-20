## Hint 1

Picture a fire that starts at every `0` at the same moment and spreads one cell per minute. When does it reach a given `1` cell? Which data structure lets you process all cells at distance 0, then all at distance 1, then distance 2, in that order?

## Hint 2

Make `dist` a new matrix filled with `-1` (meaning "not reached"). Put every `0` cell into a queue and set its distance to 0. Then run ordinary BFS: pop a cell, and for each neighbour inside the grid with `dist == -1`, set `dist = dist of the popped cell + 1` and push it.

## Hint 3

```
dist = [[-1] * cols for _ in range(rows)]
queue = deque()
for every cell (r, c) with mat[r][c] == 0: dist[r][c] = 0; queue.append((r, c))
while queue:
    r, c = queue.popleft()
    for (nr, nc) in the 4 neighbours inside the grid:
        if dist[nr][nc] == -1:
            dist[nr][nc] = dist[r][c] + 1
            queue.append((nr, nc))
return dist
```
