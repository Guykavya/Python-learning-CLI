def same(c, pc):
    return pc == "." or pc == c


def is_match(s, p):
    n, m = len(s), len(p)
    f = [[False] * (m + 1) for _ in range(n + 1)]
    f[0][0] = True
    for j in range(2, m + 1):
        if p[j - 1] == "*":
            f[0][j] = f[0][j - 2]                 # every x* so far is empty
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if p[j - 1] == "*":
                f[i][j] = f[i][j - 2] or (same(s[i - 1], p[j - 2]) and f[i - 1][j])
            else:
                f[i][j] = same(s[i - 1], p[j - 1]) and f[i - 1][j - 1]
    return f[n][m]
