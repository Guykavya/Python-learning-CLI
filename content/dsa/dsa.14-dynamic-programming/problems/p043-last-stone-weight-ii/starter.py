def last_stone_weight_ii(stones):
    """Smallest possible weight of the last stone (0 if none is left)."""
    return max(stones) - min(stones)
