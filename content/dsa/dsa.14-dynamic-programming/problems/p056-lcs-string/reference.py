def lcs_string(a, b):
    n, m = len(a), len(b)
    f = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                f[i][j] = f[i - 1][j - 1] + 1
            else:
                f[i][j] = max(f[i - 1][j], f[i][j - 1])
    i, j = n, m
    out = []
    while i > 0 and j > 0:                 # walk back from the corner
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])           # a matched character
            i -= 1
            j -= 1
        elif f[i - 1][j] >= f[i][j - 1]:
            i -= 1                         # moving up loses nothing
        else:
            j -= 1                         # moving left loses nothing
    return "".join(reversed(out))
