def max_envelopes(envelopes):
    """Most envelopes that nest (strictly smaller in width and height)."""
    return len(set(map(tuple, envelopes)))
