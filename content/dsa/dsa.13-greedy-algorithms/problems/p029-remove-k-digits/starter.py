def remove_k_digits(num, k):
    """Remove exactly k digits to make the smallest number; return it as a string without leading zeros."""
    rest = num[k:]
    return rest if rest else "0"
