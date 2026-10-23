def parse_ranges(text):
    """Turn '1-3,5,7-9' into [1, 2, 3, 5, 7, 8, 9]. Raise ValueError for bad text."""
    if text.strip() == "":
        return []
    numbers = set()
    for piece in text.split(","):
        piece = piece.strip()
        bounds = [b.strip() for b in piece.split("-")]
        if len(bounds) > 2:
            raise ValueError(f"invalid piece {piece!r}")
        for b in bounds:
            if not b.isdigit():
                raise ValueError(f"invalid piece {piece!r}")
        low = int(bounds[0])
        high = int(bounds[-1])
        if low > high:
            raise ValueError(f"reversed range {piece!r}")
        for n in range(low, high + 1):
            numbers.add(n)
    return sorted(numbers)
