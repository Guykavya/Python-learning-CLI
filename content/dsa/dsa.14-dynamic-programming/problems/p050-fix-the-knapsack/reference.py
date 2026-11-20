def knapsack(weights, values, capacity):
    """0/1 knapsack: each parcel at most once. Return the best total value."""
    best = [0] * (capacity + 1)
    for i in range(len(weights)):
        for c in range(capacity, weights[i] - 1, -1):     # downwards: best[c - w] is still old
            best[c] = max(best[c], best[c - weights[i]] + values[i])
    return best[capacity]
