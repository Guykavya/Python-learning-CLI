def power(base, exp):
    """Return base ** exp for integer exp >= 0, recursively, in O(log exp) calls."""
    if exp == 0:
        return 1
    half = power(base, exp // 2)
    if exp % 2 == 0:
        return half * half
    return half * half * base
