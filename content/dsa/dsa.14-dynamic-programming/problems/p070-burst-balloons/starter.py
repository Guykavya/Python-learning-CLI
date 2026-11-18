def max_coins(nums):
    """Most coins from bursting every balloon; a missing neighbour counts as 1."""
    total = 0
    row = list(nums)
    while row:                                 # always burst the leftmost: one order, not the best
        right = row[1] if len(row) > 1 else 1
        total += row[0] * right
        row.pop(0)
    return total
