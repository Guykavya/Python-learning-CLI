def depth(xs):
    best = 0
    for item in xs:
        if isinstance(item, list):
            best = max(best, depth(item))
    return 1 + best
