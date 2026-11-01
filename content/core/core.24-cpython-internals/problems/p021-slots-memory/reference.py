import sys


class Plain:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class Slotted:
    __slots__ = ("x", "y", "z")

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


def instance_size(obj):
    """getsizeof(obj), plus getsizeof(obj.__dict__) when the object has one."""
    size = sys.getsizeof(obj)
    if hasattr(obj, "__dict__"):
        size += sys.getsizeof(obj.__dict__)
    return size


def compare_memory(n):
    """(total bytes of n Plain instances, total bytes of n Slotted instances)."""
    plains = [Plain(i, i, i) for i in range(n)]
    slotted = [Slotted(i, i, i) for i in range(n)]
    return (
        sum(instance_size(obj) for obj in plains),
        sum(instance_size(obj) for obj in slotted),
    )
