def common_items(a, b):
    """Items of a that also appear in b, in a's order, each only once."""
    in_b = set(b)
    seen = set()
    result = []
    for x in a:
        if x in in_b and x not in seen:
            seen.add(x)
            result.append(x)
    return result
