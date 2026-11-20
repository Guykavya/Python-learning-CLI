def knapsack(weights, values, capacity):
    """0/1 knapsack: each parcel at most once. Return the best total value."""
    best = [0] * (capacity + 1)
    for i in range(len(weights)):
        for c in range(weights[i], capacity + 1):
            best[c] = max(best[c], best[c - weights[i]] + values[i])
    return best[capacity]
