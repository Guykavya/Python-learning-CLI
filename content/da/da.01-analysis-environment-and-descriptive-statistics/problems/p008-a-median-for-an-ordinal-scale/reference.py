def ordinal_median(responses, order):
    rank = {label: i for i, label in enumerate(order)}
    if not responses:
        raise ValueError("no responses")
    for r in responses:
        if r not in rank:
            raise ValueError(f"unknown label: {r!r}")
    ranks = sorted(rank[r] for r in responses)
    n, mid = len(ranks), len(ranks) // 2
    if n % 2:
        return order[ranks[mid]]
    lo, hi = ranks[mid - 1], ranks[mid]
    return order[lo] if lo == hi else (order[lo], order[hi])
