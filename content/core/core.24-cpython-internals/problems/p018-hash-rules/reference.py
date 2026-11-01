def check_hashable(obj):
    """True if hash(obj) works, False if it raises TypeError."""
    try:
        hash(obj)
    except TypeError:
        return False
    return True


class Point:
    """An immutable, hashable 2-D point."""

    __slots__ = ("x", "y")

    def __init__(self, x, y):
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "y", y)

    def __setattr__(self, name, value):
        raise AttributeError(f"Point is immutable; cannot set {name!r}")

    def __delattr__(self, name):
        raise AttributeError(f"Point is immutable; cannot delete {name!r}")

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"Point({self.x!r}, {self.y!r})"


def lost_keys(d):
    """Keys that iteration sees but a lookup no longer finds."""
    return [key for key in d if key not in d]


def hash_collisions(values):
    """Groups of non-equal values that share a hash."""
    groups = {}                       # hash -> list of pairwise non-equal values
    for value in values:
        group = groups.setdefault(hash(value), [])
        if not any(value == seen for seen in group):
            group.append(value)
    return [group for group in groups.values() if len(group) >= 2]
