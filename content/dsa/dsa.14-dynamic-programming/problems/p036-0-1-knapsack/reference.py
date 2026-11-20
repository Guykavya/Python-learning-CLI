def knapsack_table(wt, val, W):
    n = len(wt)
    f = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(W + 1):
            f[i][w] = f[i - 1][w]                                   # leave item i-1
            if wt[i - 1] <= w:
                f[i][w] = max(f[i][w], f[i - 1][w - wt[i - 1]] + val[i - 1])   # take it
    return f


def knapsack(wt, val, W):
    g = [0] * (W + 1)
    for i in range(len(wt)):
        for w in range(W, wt[i] - 1, -1):          # downwards: each item once
            g[w] = max(g[w], g[w - wt[i]] + val[i])
    return g[W]
