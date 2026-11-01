import sys


class Plain:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class Slotted:
    # TODO: __slots__ for x, y, z
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


def instance_size(obj):
    """getsizeof(obj), plus getsizeof(obj.__dict__) when the object has one."""
    # TODO: add the __dict__ when there is one
    return sys.getsizeof(obj)


def compare_memory(n):
    """(total bytes of n Plain instances, total bytes of n Slotted instances)."""
    # TODO
    return (0, 0)
