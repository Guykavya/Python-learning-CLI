def edit_ops(a, b):
    n, m = len(a), len(b)
    f = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        f[i][0] = i
    for j in range(m + 1):
        f[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                f[i][j] = f[i - 1][j - 1]
            else:
                f[i][j] = 1 + min(f[i - 1][j - 1], f[i - 1][j], f[i][j - 1])
    ops = []
    i, j = n, m
    while i > 0 or j > 0:              # right to left: positions on the left never move
        if i > 0 and j > 0 and a[i - 1] == b[j - 1] and f[i][j] == f[i - 1][j - 1]:
            i, j = i - 1, j - 1                          # keep, no operation
        elif i > 0 and j > 0 and f[i][j] == f[i - 1][j - 1] + 1:
            ops.append(("replace", i - 1, b[j - 1]))
            i, j = i - 1, j - 1
        elif i > 0 and f[i][j] == f[i - 1][j] + 1:
            ops.append(("delete", i - 1))
            i -= 1
        else:
            ops.append(("insert", i, b[j - 1]))           # right after a[:i]
            j -= 1
    return ops
