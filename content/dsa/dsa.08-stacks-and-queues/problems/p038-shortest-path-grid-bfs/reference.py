from collections import deque


def shortest_path(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    if grid[start[0]][start[1]] == "#" or grid[goal[0]][goal[1]] == "#":
        return -1
    queue = deque([(start[0], start[1], 0)])
    seen = {start}
    while queue:
        r, c, steps = queue.popleft()
        if (r, c) == goal:
            return steps
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#" and (nr, nc) not in seen:
                seen.add((nr, nc))
                queue.append((nr, nc, steps + 1))
    return -1
