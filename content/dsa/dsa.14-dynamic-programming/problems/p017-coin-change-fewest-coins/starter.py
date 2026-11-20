def coin_change(coins, amount):
    """Fewest coins (unlimited of each value) that make exactly amount, or -1."""
    count = 0
    for c in sorted(coins, reverse=True):          # greedy: biggest coin first
        count += amount // c
        amount %= c
    return count if amount == 0 else -1
