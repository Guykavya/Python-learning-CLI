def merge_counts(*counts):
    """Return a new dict of total quantities per item across all dicts, dropping zero totals."""
    totals = {}
    for one in counts:
        for item, qty in one.items():
            totals[item] = totals.get(item, 0) + qty
    return {item: q for item, q in totals.items() if q != 0}
