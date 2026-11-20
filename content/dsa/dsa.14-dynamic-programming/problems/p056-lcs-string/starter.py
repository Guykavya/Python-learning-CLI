def lcs_string(a, b):
    """One longest common subsequence of a and b."""
    return "".join(ch for ch in a if ch in b)
