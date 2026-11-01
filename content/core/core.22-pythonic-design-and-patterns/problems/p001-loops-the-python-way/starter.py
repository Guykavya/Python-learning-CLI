def indexed_lines(lines):
    """['a', 'b'] -> ['1: a', '2: b']  (numbering starts at 1)."""
    out = []
    for i in range(len(lines)):
        out.append(str(i + 1) + ": " + lines[i])
    return out


def add_lists(a, b):
    """Add two lists position by position. Stop at the shorter list."""
    out = []
    for i in range(len(a)):
        if i < len(b):
            out.append(a[i] + b[i])
    return out


def has_negative(numbers):
    """True if at least one number is below zero."""
    found = False
    for i in range(len(numbers)):
        if numbers[i] < 0:
            found = True
    return found


def count_equal_positions(a, b):
    """How many positions hold the same value in both lists (shorter list decides)."""
    count = 0
    for i in range(len(a)):
        if i < len(b) and a[i] == b[i]:
            count = count + 1
    return count
