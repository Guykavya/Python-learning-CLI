def longest_increasing_path(matrix):
    rows, cols = len(matrix), len(matrix[0])
    memo = {}

    def f(r, c):
        """Longest increasing path that starts at (r, c)."""
        if (r, c) in memo:
            return memo[(r, c)]
        best = 1
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and matrix[nr][nc] > matrix[r][c]:
                best = max(best, 1 + f(nr, nc))
        memo[(r, c)] = best
        return best

    return max(f(r, c) for r in range(rows) for c in range(cols))
