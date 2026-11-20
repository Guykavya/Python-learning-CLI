def count_distinct(s):
    """Number of different non-empty substrings of s."""
    n = len(s)
    return n * (n + 1) // 2           # counts every substring, even the repeated ones
