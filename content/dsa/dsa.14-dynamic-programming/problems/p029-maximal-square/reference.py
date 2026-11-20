def maximal_square(matrix):
    rows, cols = len(matrix), len(matrix[0])
    f = [[0] * cols for _ in range(rows)]      # fresh list per row (no aliasing)
    best = 0
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == 1:
                if r == 0 or c == 0:
                    f[r][c] = 1
                else:
                    f[r][c] = 1 + min(f[r - 1][c], f[r][c - 1], f[r - 1][c - 1])
                best = max(best, f[r][c])
    return best * best
