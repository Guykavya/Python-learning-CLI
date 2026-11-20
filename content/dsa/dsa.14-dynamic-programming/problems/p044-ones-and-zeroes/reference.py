def find_max_form(strs, m, n):
    f = [[0] * (n + 1) for _ in range(m + 1)]   # f[i][j]: at most i zeros, j ones
    for s in strs:
        z = s.count("0")
        o = s.count("1")
        for i in range(m, z - 1, -1):           # both loops downwards: each string once
            row, prev = f[i], f[i - z]
            for j in range(n, o - 1, -1):
                if prev[j - o] + 1 > row[j]:
                    row[j] = prev[j - o] + 1
    return f[m][n]
