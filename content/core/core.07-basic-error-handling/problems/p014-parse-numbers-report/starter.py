def parse_numbers(items):
    """Return (numbers, errors) for a list of texts."""
    numbers = [float(item) for item in items]
    return numbers, []
