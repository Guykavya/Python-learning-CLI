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
