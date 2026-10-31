def common_items(a, b):
    """Items of a that also appear in b, in a's order, each only once."""
    result = []
    for x in a:
        if x in b and x not in result:
            result.append(x)
    return result
