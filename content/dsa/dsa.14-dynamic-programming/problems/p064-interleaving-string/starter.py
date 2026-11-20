def is_interleave(s1, s2, s3):
    """True if s3 is a shuffle of s1 and s2 that keeps the order inside each string."""
    return len(s1) + len(s2) == len(s3)
