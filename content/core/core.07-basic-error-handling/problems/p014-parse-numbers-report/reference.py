import math


def parse_numbers(items):
    """Return (numbers, errors) for a list of texts."""
    numbers = []
    errors = []
    for n, item in enumerate(items, start=1):
        try:
            value = float(item)
        except ValueError:
            errors.append(f"item {n}: {item!r} is not a number")
            continue
        if not math.isfinite(value):
            errors.append(f"item {n}: {item!r} is not a finite number")
            continue
        numbers.append(value)
    return numbers, errors
