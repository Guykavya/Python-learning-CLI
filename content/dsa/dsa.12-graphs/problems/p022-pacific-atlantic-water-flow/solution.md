## Approach

Reverse the flow. A cell can reach the Pacific exactly when you can walk from a Pacific edge cell **up or level** to it. One multi-source search from all Pacific edge cells finds every such cell; one more from the Atlantic edges does the same for the Atlantic. The answer is the intersection.

## Code

```python
def pacific_atlantic(heights):
    if not heights or not heights[0]:
        return []
    rows, cols = len(heights), len(heights[0])

    def climb(starts):
        seen = set(starts)
        stack = list(starts)
        while stack:
            r, c = stack.pop()
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if (0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen
                        and heights[nr][nc] >= heights[r][c]):
                    seen.add((nr, nc))
                    stack.append((nr, nc))
        return seen

    pacific = [(0, c) for c in range(cols)] + [(r, 0) for r in range(rows)]
    atlantic = [(rows - 1, c) for c in range(cols)] + [(r, cols - 1) for r in range(rows)]
    return sorted(climb(pacific) & climb(atlantic))
```

## Complexity

`O(rows * cols)`: each search marks every cell at most once (sets handle the duplicated corner starts). Sorting the answer adds `O(k log k)`.

## Another way

The direct way, a downhill search from every cell, is the brute force the tests use on small grids: `O((rows * cols)^2)`. A BFS (`deque`) instead of the stack gives the same sets.
