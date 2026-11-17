## Hint 1

Treat every cell as a vertex and every pair of neighbouring cells as an edge with weight `|h[a] - h[b]|`. A route's effort is its **largest** edge weight. Which algorithm from this chapter grows routes from the start, cheapest first? What do you put in the heap instead of a summed distance?

## Hint 2

Keep `best[r][c]`, the smallest effort found so far to reach `(r, c)`. When you pop `(e, r, c)` and look at a neighbour, the effort of going there is `max(e, abs(h[r][c] - h[nr][nc]))`. If that beats `best[nr][nc]`, store it and push it. You can stop as soon as the target cell is **popped**.

## Hint 3

```
best = grid of inf;  best[0][0] = 0
heap = [(0, 0, 0)]
while heap:
    e, r, c = heappop(heap)
    if (r, c) is the target: return e
    if e > best[r][c]: continue
    for each neighbour (nr, nc) inside the grid:
        ne = max(e, abs(h[r][c] - h[nr][nc]))
        if ne < best[nr][nc]:
            best[nr][nc] = ne;  heappush(heap, (ne, nr, nc))
```
