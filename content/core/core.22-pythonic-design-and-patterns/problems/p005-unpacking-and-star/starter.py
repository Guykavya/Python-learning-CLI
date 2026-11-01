def describe_point(p):
    """p = (x, y, z) -> 'x=1, y=2, z=3'."""
    return "x=" + str(p[0]) + ", y=" + str(p[1]) + ", z=" + str(p[2])


def split_head_tail(items):
    """(first item, list of the rest). Empty input -> (None, [])."""
    if len(items) == 0:
        return None, []
    return items[0], list(items[1:])


def trim_ends(items):
    """Everything except the first and the last item. Fewer than 2 items -> []."""
    if len(items) < 2:
        return []
    return list(items[1:-1])


def swap_pairs(pairs):
    """[(1, 'a'), (2, 'b')] -> [('a', 1), ('b', 2)]."""
    out = []
    for p in pairs:
        out.append((p[1], p[0]))
    return out


def distance_between(segment):
    """segment = ((x1, y1), (x2, y2)) -> straight-line distance."""
    dx = segment[1][0] - segment[0][0]
    dy = segment[1][1] - segment[0][1]
    return (dx * dx + dy * dy) ** 0.5


def fib(n):
    """The n-th Fibonacci number: fib(0) = 0, fib(1) = 1, fib(2) = 1, fib(3) = 2."""
    a = 0
    b = 1
    for _ in range(n):
        old_a = a
        a = b
        b = old_a + b
    return a


def merge_settings(defaults, user, overrides):
    """New dict: defaults, then user, then overrides win. Inputs stay unchanged."""
    result = defaults.copy()
    result.update(user)
    result.update(overrides)
    return result
