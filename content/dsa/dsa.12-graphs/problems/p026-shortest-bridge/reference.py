from collections import deque


def shortest_bridge(grid):
    rows, cols = len(grid), len(grid[0])
    steps = ((1, 0), (-1, 0), (0, 1), (0, -1))
    start = next((r, c) for r in range(rows) for c in range(cols) if grid[r][c] == "1")
    seen = {start}
    stack, first = [start], []
    while stack:                                   # flood fill of the first island
        r, c = stack.pop()
        first.append((r, c))
        for dr, dc in steps:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen and grid[nr][nc] == "1":
                seen.add((nr, nc))
                stack.append((nr, nc))
    queue = deque((r, c, 0) for r, c in first)     # multi-source BFS
    while queue:
        r, c, d = queue.popleft()
        for dr, dc in steps:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen:
                if grid[nr][nc] == "1":
                    return d                       # the second island
                seen.add((nr, nc))
                queue.append((nr, nc, d + 1))
    return -1                                      # not reached: fewer than two islands
