def max_profit(prices):
    """Largest profit with any number of trades, at most one share held at a time."""
    if not prices:
        return 0
    return max(prices) - min(prices)
