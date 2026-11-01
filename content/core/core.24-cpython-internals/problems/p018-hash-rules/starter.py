def check_hashable(obj):
    """True if hash(obj) works, False if it raises TypeError."""
    # TODO
    return True


class Point:
    """An immutable, hashable 2-D point."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)

    # TODO: __hash__ (consistent with __eq__), immutability, __repr__


def lost_keys(d):
    """Keys that iteration sees but a lookup no longer finds."""
    # TODO
    return []


def hash_collisions(values):
    """Groups of non-equal values that share a hash."""
    # TODO
    return []
