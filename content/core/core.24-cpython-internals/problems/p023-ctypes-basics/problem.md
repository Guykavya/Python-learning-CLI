# C structs from Python with ctypes

C code stores a point as two 4-byte integers side by side:

```c
struct Point { int x; int y; };      /* 8 bytes */
```

To pass data to a C library, or to read a binary file written by a C program, you need exactly
that layout. The standard module `ctypes` lets you describe it in Python:

```python
import ctypes

class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]

p = Point(3, 4)
p.x, p.y                  # (3, 4)
ctypes.sizeof(Point)      # 8: two C ints, no Python object header counted
PointArray = Point * 3    # a C array type of 3 points (24 bytes)
arr = PointArray((1, 2), (3, 4), (5, 6))
bytes(arr)                # the raw 24 bytes
```

A C `int` has a fixed size (4 bytes on every platform Python supports), so values that do not fit
**wrap around silently**, as in C: `Point(2**31, 0).x` is `-2147483648`. Python's own `int` never
does that.

`ArrayType.from_buffer_copy(data)` builds an array from a copy of some bytes.
`ArrayType.from_buffer(buf)` builds an array that **shares memory** with a writable buffer such as a
`bytearray`: changing one changes the other.

Copy `starter.py` to `solution.py` and write (no shared library is needed or allowed: do not load
libc or any `.dll`/`.so`):

- **`class Point(ctypes.Structure)`** with `c_int` fields `x` and `y`.
- **`make_points(pairs)`**: a ctypes array of `Point` (type `Point * len(pairs)`) holding the given
  `(x, y)` pairs.
- **`sum_points(points)`**: the tuple `(sum of x, sum of y)` as Python ints, for any iterable of
  `Point`s (such as the array above).
- **`pack_points(pairs)`**: the raw bytes of `make_points(pairs)`.
- **`unpack_points(data)`**: the reverse, a list of `(x, y)` tuples. If `len(data)` is not a multiple
  of `ctypes.sizeof(Point)`, raise `ValueError`.
- **`view_points(buf)`**: a `Point` array that shares memory with the `bytearray` `buf` (same rule:
  `ValueError` if the length is not a multiple of the struct size).
- **`fits_c_int(value)`**: `True` if `value` survives a round trip through `ctypes.c_int` unchanged.

**Example**

```python
arr = make_points([(1, 2), (3, 4)])
arr[1].y, len(arr)                   # (4, 2)
sum_points(arr)                      # (4, 6)
data = pack_points([(1, 2)])
len(data)                            # 8
unpack_points(data)                  # [(1, 2)]
buf = bytearray(16)
view = view_points(buf)
view[1].x = 7
unpack_points(bytes(buf))            # [(0, 0), (7, 0)]
fits_c_int(2**31 - 1), fits_c_int(2**31)   # (True, False)
```

(The order of the bytes inside each int, "endianness", is the machine's own. All common PCs and
phones are little-endian, but the tests never depend on it.)
