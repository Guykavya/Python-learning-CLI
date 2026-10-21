def min_and_max(numbers):
    """Return (smallest, largest) of numbers, or (None, None) if it is empty."""
    if not numbers:
        return None, None
    smallest = largest = numbers[0]
    for n in numbers:
        if n < smallest:
            smallest = n
        if n > largest:
            largest = n
    return smallest, largest
