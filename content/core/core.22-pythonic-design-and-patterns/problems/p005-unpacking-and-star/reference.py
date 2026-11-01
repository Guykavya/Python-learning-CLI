def describe_point(p):
    x, y, z = p
    return f"x={x}, y={y}, z={z}"


def split_head_tail(items):
    if not items:
        return None, []
    first, *rest = items
    return first, rest


def trim_ends(items):
    if len(items) < 2:
        return []
    _, *middle, _ = items
    return middle


def swap_pairs(pairs):
    return [(b, a) for a, b in pairs]


def distance_between(segment):
    (x1, y1), (x2, y2) = segment
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def merge_settings(defaults, user, overrides):
    return defaults | user | overrides
