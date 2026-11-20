def max_coins(nums):
    a = [1] + nums + [1]
    n = len(a)
    f = [[0] * n for _ in range(n)]
    for gap in range(2, n):                    # distance between i and j: short ranges first
        for i in range(n - gap):
            j = i + gap
            f[i][j] = max(f[i][k] + f[k][j] + a[i] * a[k] * a[j]
                          for k in range(i + 1, j))
    return f[0][n - 1]
