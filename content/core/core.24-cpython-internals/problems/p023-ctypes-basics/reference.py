import ctypes


class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]


def make_points(pairs):
    """A ctypes array (Point * len(pairs)) holding the pairs."""
    array_type = Point * len(pairs)
    return array_type(*pairs)


def sum_points(points):
    """(sum of x, sum of y) as Python ints."""
    total_x = total_y = 0
    for p in points:
        total_x += p.x
        total_y += p.y
    return (total_x, total_y)


def pack_points(pairs):
    """Raw bytes of make_points(pairs)."""
    return bytes(make_points(pairs))


def _count(nbytes):
    size = ctypes.sizeof(Point)
    if nbytes % size:
        raise ValueError(f"{nbytes} bytes is not a whole number of {size}-byte points")
    return nbytes // size


def unpack_points(data):
    """List of (x, y) tuples; ValueError if len(data) is not a multiple of sizeof(Point)."""
    array = (Point * _count(len(data))).from_buffer_copy(data)
    return [(p.x, p.y) for p in array]


def view_points(buf):
    """A Point array sharing memory with the bytearray buf."""
    return (Point * _count(len(buf))).from_buffer(buf)


def fits_c_int(value):
    """True if value survives a round trip through ctypes.c_int."""
    return ctypes.c_int(value).value == value
