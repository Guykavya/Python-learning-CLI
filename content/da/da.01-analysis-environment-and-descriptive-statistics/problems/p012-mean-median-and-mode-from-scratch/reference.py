def mean(values):
    if not values:
        raise ValueError("mean of an empty list")
    return sum(values) / len(values)


def median(values):
    if not values:
        raise ValueError("median of an empty list")
    s = sorted(values)
    mid = len(s) // 2
    return s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2


def modes(values):
    if not values:
        raise ValueError("modes of an empty list")
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    top = max(counts.values())
    return sorted(v for v, c in counts.items() if c == top)
