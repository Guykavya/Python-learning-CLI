def lcs_length(a, b):
    """Length of the longest common subsequence of a and b."""
    return len(set(a) & set(b))
