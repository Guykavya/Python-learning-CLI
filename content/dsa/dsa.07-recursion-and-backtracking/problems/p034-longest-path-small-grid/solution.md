## Approach

Backtracking from every free start cell. Each call returns the longest continuation from its cell given the cells already used, so the recursion combines child answers with `max` instead of adding them. Un-marking on the way back is what lets sibling branches use the same cell.

## Code

```python
def longest_path(grid):
    rows, cols = len(grid), len(grid[0])
    free = sum(row.count(".") for row in grid)
    visited = [[False] * cols for _ in range(rows)]

    def go(r, c):
        visited[r][c] = True
        best = 0
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "." and not visited[nr][nc]:
                best = max(best, 1 + go(nr, nc))
        visited[r][c] = False
        return best

    answer = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "." and answer < free - 1:
                answer = max(answer, go(r, c))
    return answer
```

## Complexity

Exponential: all self-avoiding walks from all starts. For 16 cells this is a few hundred thousand calls. The pruning `answer < free - 1` stops as soon as a path through every free cell is found.

## Another way

Dynamic programming over bit masks: `best[mask][cell]` = can a path visit exactly the cells in `mask` and end at `cell`. That is `O(2^n * n)` states and answers the same question for up to about 20 cells.
