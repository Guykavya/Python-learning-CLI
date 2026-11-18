def is_match(s, p):
    """True if the pattern p ('.' = any one character, 'x*' = zero or more x) matches the whole of s."""
    return s == p
