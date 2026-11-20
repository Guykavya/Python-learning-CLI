def is_interleave(s1, s2, s3):
    n, m = len(s1), len(s2)
    if n + m != len(s3):
        return False
    f = [[False] * (m + 1) for _ in range(n + 1)]
    f[0][0] = True
    for i in range(n + 1):
        for j in range(m + 1):
            if i > 0 and f[i - 1][j] and s1[i - 1] == s3[i + j - 1]:
                f[i][j] = True
            if j > 0 and f[i][j - 1] and s2[j - 1] == s3[i + j - 1]:
                f[i][j] = True
    return f[n][m]
