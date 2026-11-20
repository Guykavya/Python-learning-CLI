def num_islands(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != "1" or seen[r][c]:
                continue
            count += 1
            seen[r][c] = True
            stack = [(r, c)]
            while stack:
                cr, cc = stack.pop()
                for nr, nc in ((cr - 1, cc), (cr + 1, cc), (cr, cc - 1), (cr, cc + 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1" and not seen[nr][nc]:
                        seen[nr][nc] = True
                        stack.append((nr, nc))
    return count
