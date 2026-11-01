import ctypes


class Point(ctypes.Structure):
    # TODO: _fields_ with two c_int fields, x and y
    pass


def make_points(pairs):
    """A ctypes array (Point * len(pairs)) holding the pairs."""
    # TODO
    return []


def sum_points(points):
    """(sum of x, sum of y) as Python ints."""
    # TODO
    return (0, 0)


def pack_points(pairs):
    """Raw bytes of make_points(pairs)."""
    # TODO
    return b""


def unpack_points(data):
    """List of (x, y) tuples; ValueError if len(data) is not a multiple of sizeof(Point)."""
    # TODO
    return []


def view_points(buf):
    """A Point array sharing memory with the bytearray buf."""
    # TODO: from_buffer
    return []


def fits_c_int(value):
    """True if value survives a round trip through ctypes.c_int."""
    # TODO
    return True
