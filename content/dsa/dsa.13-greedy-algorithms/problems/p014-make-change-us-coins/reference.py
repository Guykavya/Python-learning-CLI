COINS = (25, 10, 5, 1)


def make_change(amount):
    """Fewest US coins (25, 10, 5, 1) adding up to `amount`, largest first."""
    used = []
    for c in COINS:                      # already largest first
        count = amount // c              # how many of this coin fit
        used.extend([c] * count)
        amount -= count * c
    return used
