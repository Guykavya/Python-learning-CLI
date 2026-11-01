def indexed_lines(lines):
    return [f"{n}: {line}" for n, line in enumerate(lines, start=1)]


def add_lists(a, b):
    return [x + y for x, y in zip(a, b)]


def has_negative(numbers):
    return any(n < 0 for n in numbers)


def count_equal_positions(a, b):
    return sum(x == y for x, y in zip(a, b))
