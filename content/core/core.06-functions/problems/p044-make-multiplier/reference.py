def make_multiplier(factor):
    """Return a function that multiplies its argument by factor."""
    def multiply(n):
        return n * factor
    return multiply
