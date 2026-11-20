def pack_van(wt, val, W):
    n = len(wt)
    f = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(W + 1):
            f[i][w] = f[i - 1][w]
            if wt[i - 1] <= w:
                f[i][w] = max(f[i][w], f[i - 1][w - wt[i - 1]] + val[i - 1])
    items, w = [], W
    for i in range(n, 0, -1):
        if f[i][w] != f[i - 1][w]:        # the value changed, so item i-1 was taken
            items.append(i - 1)
            w -= wt[i - 1]
    items.reverse()
    return f[n][W], items
