import ctypes
import struct

import pytest

from solution import Point, fits_c_int, make_points, pack_points, sum_points, unpack_points, view_points


def native_ints(*values):
    """Bytes of C ints in this machine's own byte order (same layout as the struct)."""
    return struct.pack(f"{len(values)}i", *values)


def test_point_layout():
    assert issubclass(Point, ctypes.Structure), "Point must subclass ctypes.Structure."
    assert ctypes.sizeof(Point) == 8, "Two c_int fields: 4 + 4 = 8 bytes. Use ctypes.c_int for both."
    p = Point(3, 4)
    assert (p.x, p.y) == (3, 4), "_fields_ must be [('x', c_int), ('y', c_int)] in this order."
    assert [name for name, _ in Point._fields_] == ["x", "y"]


def test_make_points():
    arr = make_points([(1, 2), (3, 4), (5, 6)])
    assert isinstance(arr, ctypes.Array), "Return a ctypes array (Point * n)(...), not a Python list."
    assert len(arr) == 3 and ctypes.sizeof(arr) == 24, "3 points of 8 bytes each = 24 bytes, one block."
    assert (arr[2].x, arr[2].y) == (5, 6)
    assert isinstance(arr[0], Point)


def test_make_points_empty():
    arr = make_points([])
    assert len(arr) == 0 and ctypes.sizeof(arr) == 0, "No pairs: an empty Point array."


def test_sum_points():
    assert sum_points(make_points([(1, 2), (3, 4)])) == (4, 6)
    assert sum_points(make_points([])) == (0, 0)
    total = sum_points([Point(10, -1), Point(5, -2)])
    assert total == (15, -3) and all(type(v) is int for v in total), "Return plain Python ints."


def test_pack_points():
    data = pack_points([(1, 2), (3, 4)])
    assert isinstance(data, bytes), "pack_points returns bytes (bytes(array))."
    assert data == native_ints(1, 2, 3, 4), "The bytes must be x0, y0, x1, y1 as 4-byte C ints, no gaps."
    assert pack_points([]) == b""


def test_unpack_round_trip():
    pairs = [(0, 0), (-5, 7), (2**31 - 1, -(2**31))]
    assert unpack_points(pack_points(pairs)) == pairs, "unpack_points(pack_points(p)) must give p back."
    assert unpack_points(native_ints(9, 8)) == [(9, 8)]
    assert unpack_points(b"") == []


def test_unpack_bad_length():
    with pytest.raises(ValueError):
        unpack_points(b"\x00" * 12)


def test_values_wrap_like_c():
    arr = make_points([(2**31, 0)])
    assert arr[0].x == -(2**31), "Setup check: a C int silently wraps 2**31 to -2**31."
    assert not fits_c_int(2**31), "2**31 does not fit in a 4-byte signed int."
    assert fits_c_int(2**31 - 1) and fits_c_int(-(2**31)) and fits_c_int(0)
    assert not fits_c_int(-(2**31) - 1) and not fits_c_int(2**40)


def test_view_shares_memory():
    buf = bytearray(16)
    view = view_points(buf)
    assert len(view) == 2, "16 bytes hold two 8-byte points."
    view[1].x = 7
    assert bytes(buf) == native_ints(0, 0, 7, 0), (
        "Writing view[1].x must change the bytearray: use from_buffer (shares memory), not from_buffer_copy."
    )
    buf[0:4] = native_ints(42)
    assert view[0].x == 42, "And changing the bytearray must show up in the view."


def test_view_bad_length():
    with pytest.raises(ValueError):
        view_points(bytearray(10))
