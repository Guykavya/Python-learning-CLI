def squares_of_evens(numbers):
    """Return [n * n for each even n], using map and filter."""
    evens = filter(lambda n: n % 2 == 0, numbers)
    return list(map(lambda n: n * n, evens))


def parse_positive(text):
    """Return the positive integers in a whitespace-separated line, using map and filter."""
    return list(filter(lambda n: n > 0, map(int, text.split())))
