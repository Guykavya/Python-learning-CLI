def hanoi(n, source="A", target="C", spare="B"):
    """Return the list of (from, to) moves that transfer n discs from source to target."""
    if n == 0:
        return []
    return (hanoi(n - 1, source, spare, target)
            + [(source, target)]
            + hanoi(n - 1, spare, target, source))
