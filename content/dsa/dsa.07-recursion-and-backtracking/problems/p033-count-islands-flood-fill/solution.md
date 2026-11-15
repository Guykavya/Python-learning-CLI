## Approach

Every land cell belongs to exactly one island. The outer loop finds the first cell of each island; the fill marks the rest. The recursive fill is the clearest version, but its depth can be as large as the island; an explicit stack holds the cells still to explore in a list instead of in Python frames, so it has no depth limit.

## Code

The recursive fill (correct, but fails on the snake):

```python
def count_islands(grid):
    rows, cols = len(grid), len(grid[0])
    seen = set()

    def fill(r, c):
        if not (0 <= r < rows and 0 <= c < cols) or grid[r][c] != "#" or (r, c) in seen:
            return
        seen.add((r, c))
        fill(r + 1, c); fill(r - 1, c); fill(r, c + 1); fill(r, c - 1)

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "#" and (r, c) not in seen:
                count += 1
                fill(r, c)
    return count
```

The explicit-stack version, which passes everything:

```python
def count_islands(grid):
    rows, cols = len(grid), len(grid[0])
    seen = set()
    count = 0
    for r0 in range(rows):
        for c0 in range(cols):
            if grid[r0][c0] != "#" or (r0, c0) in seen:
                continue
            count += 1
            seen.add((r0, c0))
            stack = [(r0, c0)]
            while stack:
                r, c = stack.pop()
                for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "#" and (nr, nc) not in seen:
                        seen.add((nr, nc))
                        stack.append((nr, nc))
    return count
```

## Complexity

`O(rows * cols)`: every cell is pushed and visited at most once. The recursive version needs stack depth up to the island size; the loop version needs a list of up to that size instead.

## Another way

Use `collections.deque` and `popleft()` for a breadth-first fill (same count), or union-find over the land cells.
