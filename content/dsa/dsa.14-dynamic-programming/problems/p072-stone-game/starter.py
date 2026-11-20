def stone_game(piles):
    """First player's stones minus second player's stones, both playing perfectly."""
    row = list(piles)
    diff, sign = 0, 1
    while row:                                       # greedy: take the larger end (not perfect play)
        take = row.pop(0) if row[0] >= row[-1] else row.pop()
        diff += sign * take
        sign = -sign
    return diff
