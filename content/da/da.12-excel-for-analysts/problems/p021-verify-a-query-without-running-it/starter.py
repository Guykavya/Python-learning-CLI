def fingerprint_table(df, keys=()):
    """dict: rows, columns, sum(c) for numeric columns, blank(c) for every column, distinct(k) for the keys."""
    raise NotImplementedError


def compare_fingerprints(a, b):
    """Plain-words differences between two fingerprints (see the statement for the order and the wording)."""
    raise NotImplementedError
