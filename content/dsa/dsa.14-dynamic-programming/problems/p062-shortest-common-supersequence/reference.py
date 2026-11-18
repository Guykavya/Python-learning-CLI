def lcs_table(a, b):
    n, m = len(a), len(b)
    f = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                f[i][j] = f[i - 1][j - 1] + 1
            else:
                f[i][j] = max(f[i - 1][j], f[i][j - 1])
    return f


def shortest_supersequence(a, b):
    f = lcs_table(a, b)
    i, j = len(a), len(b)
    out = []
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])            # shared letter: written once
            i -= 1
            j -= 1
        elif f[i - 1][j] >= f[i][j - 1]:
            out.append(a[i - 1])            # a[i-1] is not shared on this path
            i -= 1
        else:
            out.append(b[j - 1])
            j -= 1
    while i > 0:
        out.append(a[i - 1])
        i -= 1
    while j > 0:
        out.append(b[j - 1])
        j -= 1
    return "".join(reversed(out))
