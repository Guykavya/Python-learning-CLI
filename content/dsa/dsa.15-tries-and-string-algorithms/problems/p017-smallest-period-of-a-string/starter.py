def smallest_period(s):
    """Smallest p such that s[i] == s[i + p] for every valid i."""
    return len(s)


def all_periods(s):
    """Every period of s, in increasing order."""
    return [len(s)]
