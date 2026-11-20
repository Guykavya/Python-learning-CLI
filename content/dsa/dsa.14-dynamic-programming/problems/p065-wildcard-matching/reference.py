def wildcard_match(s, p):
    n, m = len(s), len(p)
    f = [[False] * (m + 1) for _ in range(n + 1)]
    f[0][0] = True
    for j in range(1, m + 1):
        f[0][j] = f[0][j - 1] and p[j - 1] == "*"       # only stars can match ""
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if p[j - 1] == "*":
                f[i][j] = f[i][j - 1] or f[i - 1][j]     # empty, or eat s[i-1] and stay
            elif p[j - 1] == "?" or p[j - 1] == s[i - 1]:
                f[i][j] = f[i - 1][j - 1]
    return f[n][m]
