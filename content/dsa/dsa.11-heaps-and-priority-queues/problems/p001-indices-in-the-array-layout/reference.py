def parent(i):
    return (i - 1) // 2


def left(i):
    return 2 * i + 1


def right(i):
    return 2 * i + 2


def children(i, n):
    return [c for c in (left(i), right(i)) if c < n]
