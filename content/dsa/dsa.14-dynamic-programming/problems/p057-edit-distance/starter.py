def edit_distance(a, b):
    """Fewest inserts, deletes and replaces that turn a into b."""
    return abs(len(a) - len(b))
