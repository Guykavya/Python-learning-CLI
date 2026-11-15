## Approach

Every all-1 rectangle has a bottom row. Standing on that row, each of its columns has at least the rectangle's height of consecutive 1s above and including the row, so the rectangle fits under the row's histogram. Conversely every rectangle under the histogram is all 1s. So the answer is the maximum over rows of "largest rectangle in this row's histogram". The heights are updated row by row in `O(cols)`.

## Code

```python
def largest_rectangle(heights):
    stack = []
    best = 0
    for i, h in enumerate(heights + [0]):
        while stack and heights[stack[-1]] >= h:
            height = heights[stack.pop()]
            left = stack[-1] if stack else -1
            best = max(best, height * (i - left - 1))
        stack.append(i)
    return best


def histograms(grid):
    cols = len(grid[0]) if grid else 0
    h = [0] * cols
    rows = []
    for row in grid:
        h = [h[c] + 1 if row[c] == "1" else 0 for c in range(cols)]
        rows.append(h)
    return rows


def maximal_rectangle(grid):
    best = 0
    for h in histograms(grid):
        best = max(best, largest_rectangle(h))
    return best
```

## Complexity

`O(rows * cols)` time: each row costs `O(cols)` for the heights and `O(cols)` for the histogram. Memory `O(rows * cols)` here because `histograms` keeps every row; `maximal_rectangle` alone needs only `O(cols)` if you update one list.

## Another way

Brute force over all pairs of rows `(top, bottom)`: AND the rows together column by column and find the longest run of 1s. That is `O(rows^2 * cols)`; fine for small grids, and a good check for your fast version.
