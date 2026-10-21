def append_total(numbers):
    """Append sum(numbers) to the end of numbers, in place. Return None."""
    numbers = numbers + [sum(numbers)]
