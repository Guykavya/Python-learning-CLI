def fractional_knapsack(items, capacity):
    """Largest total value of (value, weight) piles that fits, when fractions are allowed."""
    total = 0.0
    room = capacity
    for value, weight in sorted(items, key=lambda it: it[0] / it[1], reverse=True):
        if room <= 0:
            break
        part = min(weight, room)              # the whole pile, or whatever still fits
        total += value * part / weight
        room -= part
    return total
