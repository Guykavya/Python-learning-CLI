def lcs_length(a, b):
    n, m = len(a), len(b)
    f = [[0] * (m + 1) for _ in range(n + 1)]     # f[i][j]: LCS of a[:i] and b[:j]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                f[i][j] = f[i - 1][j - 1] + 1      # match the last characters
            else:
                f[i][j] = max(f[i - 1][j], f[i][j - 1])
    return f[n][m]
