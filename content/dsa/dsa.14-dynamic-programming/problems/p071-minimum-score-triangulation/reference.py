def min_score_triangulation(values):
    n = len(values)
    f = [[0] * n for _ in range(n)]
    for gap in range(2, n):                     # short pieces first
        for i in range(n - gap):
            j = i + gap
            f[i][j] = min(f[i][k] + f[k][j] + values[i] * values[k] * values[j]
                          for k in range(i + 1, j))
    return f[0][n - 1]
