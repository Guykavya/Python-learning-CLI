def num_distinct(s, t):
    n, m = len(s), len(t)
    f = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        f[i][0] = 1                              # empty t: one way
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            f[i][j] = f[i - 1][j]                # do not use s[i-1]
            if s[i - 1] == t[j - 1]:
                f[i][j] += f[i - 1][j - 1]       # use s[i-1] for t[j-1]
    return f[n][m]
