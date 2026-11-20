def greedy_count(amount, coins_desc):
    count = 0
    for c in coins_desc:
        count += amount // c
        amount %= c
    return count


def is_canonical(coins):
    """True if largest-coin-first pays every amount with the fewest coins (coins contain 1)."""
    coins = sorted(coins)
    if len(coins) < 2:
        return True                                   # only the 1 coin: one way to pay
    limit = coins[-1] + coins[-2] - 1                 # the first failure, if any, is <= limit
    desc = coins[::-1]
    best = [0] * (limit + 1)                          # best[a] = fewest coins for amount a
    for a in range(1, limit + 1):
        best[a] = 1 + min(best[a - c] for c in coins if c <= a)
        if greedy_count(a, desc) != best[a]:
            return False
    return True
