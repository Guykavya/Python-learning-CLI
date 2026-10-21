def drop_negatives(numbers):
    """Remove every negative number from numbers, in place. Return None."""
    numbers = [n for n in numbers if n >= 0]
