def unbounded_knapsack(wt, val, W):
    g = [0] * (W + 1)
    for i in range(len(wt)):
        for w in range(wt[i], W + 1):            # upwards: the item may repeat
            g[w] = max(g[w], g[w - wt[i]] + val[i])
    return g[W]
