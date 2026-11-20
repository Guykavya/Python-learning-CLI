## Hint 1

Searching downhill from each of the 90,000 cells repeats the same work again and again. Think backwards: instead of "where can water from this cell go?", ask "which cells can send water **to** the Pacific?". Water flows from `a` to a neighbour `b` when `height[b] <= height[a]`. If you walk **against** the flow, from `b` to `a`, which height condition do you need?

## Hint 2

Two multi-source searches (chapter section 3):

```
pac = search starting from all cells of the top row and the left column
atl = search starting from all cells of the bottom row and the right column
search: from (r, c) step to a neighbour (nr, nc) if heights[nr][nc] >= heights[r][c]   # uphill or level
answer = sorted(pac & atl)
```
