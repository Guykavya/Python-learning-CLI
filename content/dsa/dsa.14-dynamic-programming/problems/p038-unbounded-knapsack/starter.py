def unbounded_knapsack(wt, val, W):
    """Best total value with total weight <= W; every item may be taken any number of times."""
    g = [0] * (W + 1)
    for i in range(len(wt)):
        for w in range(W, wt[i] - 1, -1):
            g[w] = max(g[w], g[w - wt[i]] + val[i])
    return g[W]
