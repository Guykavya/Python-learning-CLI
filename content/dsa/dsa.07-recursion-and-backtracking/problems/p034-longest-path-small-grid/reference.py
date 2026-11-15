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
