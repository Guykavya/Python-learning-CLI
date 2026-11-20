def matrix_chain_cost(dims):
    n = len(dims) - 1                       # number of matrices
    f = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):          # short ranges first
        for i in range(n - length + 1):
            j = i + length - 1
            f[i][j] = min(f[i][k] + f[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                          for k in range(i, j))
    return f[0][n - 1]
