def knapsack_table(wt, val, W):
    """Full table: f[i][w] = best value with the first i items and capacity w (len(wt) + 1 rows)."""
    return [[0] * (W + 1) for _ in range(len(wt) + 1)]


def knapsack(wt, val, W):
    """Best total value, each item at most once, using one list of W + 1 numbers."""
    return 0
